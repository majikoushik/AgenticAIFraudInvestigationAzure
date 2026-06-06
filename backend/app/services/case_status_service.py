from app.core.constants import ALLOWED_STATUS_TRANSITIONS, AuditEventType, CaseStatus, ReviewerRole
from app.repositories.case_repository import CaseRepository
from app.services.errors import ApiError


class CaseStatusService:
    def __init__(self, repository: CaseRepository | None = None) -> None:
        self._statuses: dict[str, CaseStatus] = {}
        self.repository = repository or CaseRepository()

    def is_transition_allowed(self, current_status: str, target_status: str) -> bool:
        current = self._parse_status(current_status)
        target = self._parse_status(target_status)
        return target in ALLOWED_STATUS_TRANSITIONS.get(current, set())

    def validate_transition(self, current_status: str, target_status: str) -> None:
        current = self._parse_status(current_status)
        target = self._parse_status(target_status)
        if current == CaseStatus.CLOSED:
            raise ApiError(400, "case_closed", "Case is already CLOSED and cannot be modified.")
        if target not in ALLOWED_STATUS_TRANSITIONS.get(current, set()):
            raise ApiError(
                400,
                "invalid_status_transition",
                f"Invalid status transition from {current.value} to {target.value}",
            )

    def get_allowed_next_statuses(self, current_status: str) -> list[str]:
        current = self._parse_status(current_status)
        return sorted(status.value for status in ALLOWED_STATUS_TRANSITIONS.get(current, set()))

    def get_status(self, case_id: str, initial_status: str | None = None) -> CaseStatus:
        if case_id not in self._statuses:
            case = self.repository.get_case_by_id(case_id)
            self._statuses[case_id] = self._normalize_status(case.get("status") if case else initial_status)
        return self._statuses[case_id]

    def set_initial_status(self, case_id: str, initial_status: str | None) -> None:
        self._statuses.setdefault(case_id, self._normalize_status(initial_status))

    def transition(self, case_id: str, current_status: CaseStatus, new_status: CaseStatus) -> tuple[CaseStatus, CaseStatus]:
        self.validate_transition(current_status.value, new_status.value)
        self._statuses[case_id] = new_status
        self.repository.update_case_status(case_id, new_status.value, "system")
        return current_status, new_status

    def transition_case_status(
        self,
        case_id: str,
        target_status: str,
        actor: str = "system",
        actor_role: str = "SYSTEM",
        comment: str | None = None,
    ) -> dict:
        case = self.repository.get_case_by_id(case_id)
        if case is None:
            raise ApiError(404, "case_not_found", f"Case '{case_id}' was not found.")

        current_status = self.get_status(case_id, case.get("status"))
        target = self._parse_status(target_status)
        self.validate_transition(current_status.value, target.value)
        updated_case = self.repository.update_case_status(case_id, target.value, actor, comment)
        self._statuses[case_id] = target

        from app.services.audit_service import audit_service

        audit_service.record_event(
            case_id=case_id,
            event_type=self._event_type_for_transition(current_status, target),
            actor=actor,
            actor_role=self._parse_actor_role(actor_role),
            previous_status=current_status.value,
            new_status=target.value,
            comment=comment,
            metadata={"transition_allowed": True},
        )
        return {
            "case_id": case_id,
            "previous_status": current_status.value,
            "new_status": target.value,
            "allowed_next_statuses": self.get_allowed_next_statuses(target.value),
            "status_updated_at": updated_case.get("status_updated_at"),
            "status_updated_by": updated_case.get("status_updated_by"),
            "status_comment": updated_case.get("status_comment"),
            "message": "Case status updated successfully",
        }

    def force_status(self, case_id: str, new_status: CaseStatus) -> None:
        self._statuses[case_id] = new_status
        try:
            self.repository.update_case_status(case_id, new_status.value, "test")
        except KeyError:
            pass

    @staticmethod
    def _parse_status(status: str) -> CaseStatus:
        try:
            return CaseStatus(status.upper())
        except ValueError as exc:
            raise ApiError(400, "invalid_status", f"Unknown case status '{status}'.") from exc

    @staticmethod
    def _normalize_status(status: str | None) -> CaseStatus:
        if not status:
            return CaseStatus.NEW
        normalized = status.upper()
        legacy_map = {
            "AWAITING_HUMAN_REVIEW": CaseStatus.PENDING_HUMAN_REVIEW,
            "TRIAGE": CaseStatus.NEW,
        }
        if normalized in legacy_map:
            return legacy_map[normalized]
        try:
            return CaseStatus(normalized)
        except ValueError:
            return CaseStatus.NEW

    @staticmethod
    def _parse_actor_role(actor_role: str) -> ReviewerRole:
        try:
            return ReviewerRole(actor_role.upper())
        except ValueError:
            return ReviewerRole.SYSTEM

    @staticmethod
    def _event_type_for_transition(current_status: CaseStatus, target_status: CaseStatus) -> AuditEventType:
        if target_status == CaseStatus.AI_INVESTIGATION_IN_PROGRESS:
            return AuditEventType.AI_INVESTIGATION_STARTED
        if target_status == CaseStatus.AI_INVESTIGATION_COMPLETED:
            return AuditEventType.AI_INVESTIGATION_COMPLETED
        if target_status == CaseStatus.PENDING_HUMAN_REVIEW:
            return AuditEventType.PENDING_HUMAN_REVIEW_SET
        if target_status == CaseStatus.CLOSED:
            return AuditEventType.CASE_CLOSED
        return AuditEventType.CASE_STATUS_CHANGED


case_status_service = CaseStatusService()
