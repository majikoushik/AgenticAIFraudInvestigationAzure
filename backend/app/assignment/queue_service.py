from datetime import datetime
from typing import Any

from app.assignment.assignment_repository import AssignmentRepository
from app.assignment.sla_service import SlaService


PRIORITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
SLA_RANK = {"BREACHED": 0, "AT_RISK": 1, "ON_TRACK": 2, "NOT_APPLICABLE": 3}


class QueueService:
    def __init__(self, repository: AssignmentRepository | None = None, sla_service: SlaService | None = None) -> None:
        self.repository = repository or AssignmentRepository()
        self.sla_service = sla_service or SlaService(self.repository)

    def get_my_queue(self, user_id: str, filters: dict | None = None) -> dict:
        cases = self.repository.list_cases_assigned_to(user_id)
        return self._response("my_queue", cases, filters)

    def get_unassigned_queue(self, filters: dict | None = None) -> dict:
        return self._response("unassigned_queue", self.repository.list_unassigned_cases(), filters)

    def get_team_queue(self, team: str | None = None, filters: dict | None = None) -> dict:
        cases = self.repository.list_cases_by_team(team) if team else self.repository.list_cases()
        return self._response("team_queue", cases, filters)

    def get_escalated_queue(self, filters: dict | None = None) -> dict:
        cases = [case for case in self.repository.list_cases() if str(case.get("status")).upper() == "ESCALATED"]
        return self._response("escalated_queue", cases, filters)

    def get_sla_risk_queue(self, filters: dict | None = None) -> dict:
        cases = [case for case in self.repository.list_cases() if self.sla_service.calculate_sla_status(case.get("sla_due_at")) in {"AT_RISK", "BREACHED"}]
        return self._response("sla_risk_queue", cases, filters)

    def _response(self, name: str, cases: list[dict[str, Any]], filters: dict | None) -> dict:
        applied_filters = {key: value for key, value in (filters or {}).items() if value not in {None, ""}}
        filtered = self._apply_filters(cases, applied_filters)
        sorted_cases = self._sort(filtered, applied_filters.get("sort_by"), applied_filters.get("sort_order"))
        rows = [self._to_queue_case(case) for case in sorted_cases]
        return {"queue_name": name, "count": len(rows), "cases": rows, "filters": applied_filters}

    def _apply_filters(self, cases: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
        result = cases
        for source_key, target_key in (
            ("status", "assignment_status"),
            ("assignment_priority", "assignment_priority"),
            ("priority", "assignment_priority"),
            ("sla_status", "sla_status"),
            ("risk_level", "severity"),
            ("assigned_team", "assigned_team"),
        ):
            value = filters.get(source_key)
            if value:
                result = [case for case in result if str(case.get(target_key) or "").upper() == str(value).upper()]
        if filters.get("created_after"):
            result = [case for case in result if str(case.get("created_at") or "") >= str(filters["created_after"])]
        if filters.get("created_before"):
            result = [case for case in result if str(case.get("created_at") or "") <= str(filters["created_before"])]
        return result

    def _sort(self, cases: list[dict[str, Any]], sort_by: str | None, sort_order: str | None) -> list[dict[str, Any]]:
        reverse = str(sort_order or "").lower() == "desc"
        if sort_by:
            return sorted(cases, key=lambda case: str(case.get(sort_by) or ""), reverse=reverse)
        return sorted(cases, key=lambda case: (
            PRIORITY_RANK.get(str(case.get("assignment_priority") or "MEDIUM").upper(), 2),
            SLA_RANK.get(str(self.sla_service.calculate_sla_status(case.get("sla_due_at"))), 3),
            self._parse_created_at(case.get("created_at")),
        ))

    def _to_queue_case(self, case: dict[str, Any]) -> dict[str, Any]:
        return {
            "case_id": case["case_id"],
            "alert_id": case["alert_id"],
            "alert_type": case.get("reason") or "Fraud alert",
            "risk_level": case.get("severity") or "medium",
            "case_status": case.get("status") or "NEW",
            "assignment_status": case.get("assignment_status") or "UNASSIGNED",
            "assigned_to": case.get("assigned_to"),
            "assigned_to_name": case.get("assigned_to_name"),
            "assigned_team": case.get("assigned_team"),
            "assignment_priority": case.get("assignment_priority") or "MEDIUM",
            "sla_status": self.sla_service.calculate_sla_status(case.get("sla_due_at")),
            "sla_due_at": case.get("sla_due_at"),
            "created_at": case.get("created_at"),
            "reason": case.get("reason") or "",
        }

    @staticmethod
    def _parse_created_at(value: str | None) -> datetime:
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return datetime.min
