from typing import Any

from app.core.constants import AssignmentPriority, AssignmentStatus, SlaStatus
from app.repositories.case_repository import CaseRepository


def priority_from_case(case: dict[str, Any]) -> str:
    severity = str(case.get("severity") or "").upper()
    if "CRITICAL" in severity:
        return AssignmentPriority.CRITICAL.value
    if "HIGH" in severity:
        return AssignmentPriority.HIGH.value
    if "LOW" in severity:
        return AssignmentPriority.LOW.value
    return AssignmentPriority.MEDIUM.value


def normalize_assignment_fields(case: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(case)
    normalized.setdefault("assigned_to", None)
    normalized.setdefault("assigned_to_name", None)
    normalized.setdefault("assigned_to_role", None)
    normalized.setdefault("assigned_team", "Fraud Operations")
    normalized.setdefault("assigned_by", None)
    normalized.setdefault("assigned_at", None)
    normalized.setdefault("assignment_status", AssignmentStatus.UNASSIGNED.value if not normalized.get("assigned_to") else AssignmentStatus.ASSIGNED.value)
    normalized.setdefault("assignment_priority", priority_from_case(normalized))
    normalized.setdefault("sla_due_at", None)
    normalized.setdefault("sla_status", SlaStatus.NOT_APPLICABLE.value)
    normalized.setdefault("last_assignment_action", None)
    return normalized


class AssignmentRepository:
    def __init__(self, case_repository: CaseRepository | None = None) -> None:
        self.case_repository = case_repository or CaseRepository()

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        case = self.case_repository.get_case_by_id(case_id)
        return normalize_assignment_fields(case) if case else None

    def update_case_assignment(self, case_id: str, assignment_updates: dict[str, Any]) -> dict[str, Any]:
        return normalize_assignment_fields(self.case_repository.update_case_fields(case_id, assignment_updates))

    def list_cases(self) -> list[dict[str, Any]]:
        return [normalize_assignment_fields(case) for case in self.case_repository.list_alerts()]

    def list_unassigned_cases(self) -> list[dict[str, Any]]:
        return [case for case in self.list_cases() if not case.get("assigned_to") or case.get("assignment_status") in {AssignmentStatus.UNASSIGNED.value, AssignmentStatus.RELEASED.value}]

    def list_cases_assigned_to(self, user_id: str) -> list[dict[str, Any]]:
        return [case for case in self.list_cases() if case.get("assigned_to") == user_id]

    def list_cases_by_team(self, team: str) -> list[dict[str, Any]]:
        return [case for case in self.list_cases() if str(case.get("assigned_team") or "").lower() == team.lower()]
