from datetime import UTC, datetime
from typing import Any

from app.assignment import assignment_permissions
from app.assignment.assignment_config import assignment_config
from app.assignment.assignment_history_service import AssignmentHistoryService
from app.assignment.assignment_repository import AssignmentRepository
from app.assignment.sla_service import SlaService
from app.auth.current_user import AuthenticatedUser
from app.core.constants import AssignmentStatus, AuditEventType, CaseStatus, ReviewerRole
from app.observability.telemetry_client import get_telemetry_client
from app.observability import telemetry_events
from app.notifications.integrations.assignment_notifications import notify_assignment_event
from app.schemas.assignment_schema import (
    CaseAcceptRequest,
    CaseAssignmentRequest,
    CaseReassignmentRequest,
    CaseReleaseRequest,
    CaseTransferRequest,
)
from app.services.audit_service import AuditService, audit_service
from app.services.errors import ApiError


class AssignmentService:
    def __init__(
        self,
        repository: AssignmentRepository | None = None,
        history_service: AssignmentHistoryService | None = None,
        sla_service: SlaService | None = None,
        audit: AuditService | None = None,
    ) -> None:
        self.repository = repository or AssignmentRepository()
        self.history_service = history_service or AssignmentHistoryService()
        self.sla_service = sla_service or SlaService(self.repository)
        self.audit_service = audit or audit_service
        self.config = assignment_config

    def assign_case(self, request: CaseAssignmentRequest, actor_user: AuthenticatedUser) -> dict:
        case_id = request.case_id
        if not case_id:
            raise ApiError(400, "case_id_required", "Case ID is required.")
        case = self._ensure_assignable(case_id)
        assignment_permissions.ensure_can_assign(actor_user, case, request.assigned_to)
        now = datetime.now(UTC)
        sla_due_at = request.sla_due_at or (self.sla_service.calculate_sla_due_at(request.assignment_priority.value, now) if self.config.auto_set_sla_on_assignment else None)
        updates = {
            "assigned_to": request.assigned_to,
            "assigned_to_name": request.assigned_to_name,
            "assigned_to_role": request.assigned_to_role,
            "assigned_team": request.assigned_team,
            "assigned_by": actor_user.user_id,
            "assigned_at": now.isoformat(),
            "assignment_status": AssignmentStatus.ASSIGNED.value,
            "assignment_priority": request.assignment_priority.value,
            "sla_due_at": sla_due_at.isoformat() if sla_due_at else None,
            "sla_status": self.sla_service.calculate_sla_status(sla_due_at),
            "last_assignment_action": "ASSIGNED",
        }
        updated = self.repository.update_case_assignment(case_id, updates)
        self._record_action("ASSIGNED", case, updated, actor_user, request.comment, AuditEventType.CASE_ASSIGNED)
        notify_assignment_event("CASE_ASSIGNED", updated)
        return self._response(updated, "Case assigned.")

    def reassign_case(self, case_id: str, request: CaseReassignmentRequest, actor_user: AuthenticatedUser) -> dict:
        case = self._ensure_assignable(case_id)
        assignment_permissions.ensure_can_reassign(actor_user)
        now = datetime.now(UTC)
        priority = request.assignment_priority.value if request.assignment_priority else case.get("assignment_priority", self.config.default_assignment_priority)
        sla_due_at = request.sla_due_at or case.get("sla_due_at")
        updates = {
            "assigned_to": request.assigned_to,
            "assigned_to_name": request.assigned_to_name,
            "assigned_to_role": request.assigned_to_role,
            "assigned_team": request.assigned_team,
            "assigned_by": actor_user.user_id,
            "assigned_at": now.isoformat(),
            "assignment_status": AssignmentStatus.ASSIGNED.value,
            "assignment_priority": priority,
            "sla_due_at": self._iso(sla_due_at),
            "sla_status": self.sla_service.calculate_sla_status(sla_due_at),
            "last_assignment_action": "REASSIGNED",
        }
        updated = self.repository.update_case_assignment(case_id, updates)
        self._record_action("REASSIGNED", case, updated, actor_user, request.comment, AuditEventType.CASE_REASSIGNED)
        notify_assignment_event("CASE_REASSIGNED", updated)
        return self._response(updated, "Case reassigned.")

    def accept_case(self, case_id: str, request: CaseAcceptRequest, actor_user: AuthenticatedUser) -> dict:
        case = self._ensure_assignable(case_id)
        assignment_permissions.ensure_can_accept(actor_user, case, request.accepted_by)
        updates: dict[str, Any] = {
            "assigned_to": case.get("assigned_to") or request.accepted_by,
            "assigned_to_name": case.get("assigned_to_name") or actor_user.display_name or request.accepted_by,
            "assigned_to_role": case.get("assigned_to_role") or actor_user.primary_role,
            "assigned_team": case.get("assigned_team") or self.config.default_assignment_team,
            "assignment_status": AssignmentStatus.ACCEPTED.value,
            "last_assignment_action": "ACCEPTED",
        }
        if not case.get("assigned_at"):
            now = datetime.now(UTC)
            updates["assigned_at"] = now.isoformat()
            updates["assigned_by"] = actor_user.user_id
            if self.config.auto_set_sla_on_assignment and not case.get("sla_due_at"):
                due_at = self.sla_service.calculate_sla_due_at(case.get("assignment_priority", self.config.default_assignment_priority), now)
                updates["sla_due_at"] = due_at.isoformat()
                updates["sla_status"] = self.sla_service.calculate_sla_status(due_at)
        updated = self.repository.update_case_assignment(case_id, updates)
        self._record_action("ACCEPTED", case, updated, actor_user, request.comment, AuditEventType.CASE_ACCEPTED)
        notify_assignment_event("CASE_ACCEPTED", updated)
        return self._response(updated, "Case accepted.")

    def release_case(self, case_id: str, request: CaseReleaseRequest, actor_user: AuthenticatedUser) -> dict:
        case = self._ensure_assignable(case_id)
        assignment_permissions.ensure_can_release(actor_user, case, request.released_by)
        updates = {
            "assigned_to": None,
            "assigned_to_name": None,
            "assigned_to_role": None,
            "assigned_by": None,
            "assigned_at": None,
            "assignment_status": AssignmentStatus.UNASSIGNED.value,
            "sla_due_at": None,
            "sla_status": "NOT_APPLICABLE",
            "last_assignment_action": "RELEASED",
        }
        updated = self.repository.update_case_assignment(case_id, updates)
        self._record_action("RELEASED", case, updated, actor_user, request.comment or request.reason, AuditEventType.CASE_RELEASED)
        notify_assignment_event("CASE_RELEASED", updated)
        return self._response(updated, "Case released to unassigned queue.")

    def transfer_case(self, case_id: str, request: CaseTransferRequest, actor_user: AuthenticatedUser) -> dict:
        assignment_permissions.ensure_can_transfer(actor_user)
        reassignment = CaseReassignmentRequest(**request.model_dump())
        response = self.reassign_case(case_id, reassignment, actor_user)
        case = response["case"]
        case["last_assignment_action"] = "TRANSFERRED"
        case["assignment_status"] = AssignmentStatus.TRANSFERRED.value
        updated = self.repository.update_case_assignment(case_id, {"last_assignment_action": "TRANSFERRED", "assignment_status": AssignmentStatus.TRANSFERRED.value})
        self._record_action("TRANSFERRED", self.repository.get_case(case_id) or {}, updated, actor_user, request.comment, AuditEventType.CASE_TRANSFERRED)
        notify_assignment_event("CASE_TRANSFERRED", updated)
        return self._response(updated, "Case transferred.")

    def get_assignment_history(self, case_id: str, actor_user: AuthenticatedUser | None = None) -> dict:
        case = self._ensure_exists(case_id)
        if actor_user:
            assignment_permissions.ensure_can_view_history(actor_user, case)
        history = self.history_service.list_history_by_case(case_id)
        return {"case_id": case_id, "count": len(history), "history": history}

    def _ensure_exists(self, case_id: str) -> dict[str, Any]:
        case = self.repository.get_case(case_id)
        if not case:
            raise ApiError(404, "case_not_found", f"Case '{case_id}' was not found.")
        return case

    def _ensure_assignable(self, case_id: str) -> dict[str, Any]:
        case = self._ensure_exists(case_id)
        if str(case.get("status") or "").upper() == CaseStatus.CLOSED.value:
            raise ApiError(400, "closed_case_assignment_not_allowed", "Closed cases cannot be assigned or modified.")
        return case

    def _record_action(self, action: str, previous: dict, updated: dict, actor_user: AuthenticatedUser, comment: str | None, event_type: AuditEventType) -> None:
        self.history_service.append_history_record({
            "case_id": updated["case_id"],
            "action": action,
            "previous_assigned_to": previous.get("assigned_to"),
            "new_assigned_to": updated.get("assigned_to"),
            "actor": actor_user.user_id,
            "actor_role": actor_user.primary_role,
            "comment": comment,
        })
        self.audit_service.record_event(
            case_id=updated["case_id"],
            event_type=event_type,
            actor=actor_user.user_id,
            actor_role=ReviewerRole(actor_user.primary_role),
            comment=comment,
            metadata={
                "previous_assigned_to": previous.get("assigned_to"),
                "new_assigned_to": updated.get("assigned_to"),
                "assigned_team": updated.get("assigned_team"),
                "assignment_priority": updated.get("assignment_priority"),
                "sla_due_at": updated.get("sla_due_at"),
                "sla_status": updated.get("sla_status"),
            },
        )
        try:
            get_telemetry_client().track_event(getattr(telemetry_events, f"CASE_{action}", event_type.value), {"case_id": updated["case_id"], "actor_role": actor_user.primary_role})
        except Exception:
            return None

    @staticmethod
    def _response(case: dict[str, Any], message: str) -> dict:
        return {"case_id": case["case_id"], "message": message, "assignment": {key: case.get(key) for key in (
            "assigned_to", "assigned_to_name", "assigned_to_role", "assigned_team", "assigned_by", "assigned_at",
            "assignment_status", "assignment_priority", "sla_due_at", "sla_status", "last_assignment_action"
        )}, "case": case}

    @staticmethod
    def _iso(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
