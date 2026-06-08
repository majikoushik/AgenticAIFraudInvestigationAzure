from datetime import UTC, datetime, timedelta
from typing import Any

from app.assignment.assignment_config import assignment_config
from app.assignment.assignment_repository import AssignmentRepository
from app.core.constants import SlaStatus


class SlaService:
    def __init__(self, repository: AssignmentRepository | None = None) -> None:
        self.repository = repository or AssignmentRepository()
        self.config = assignment_config

    def calculate_sla_due_at(self, priority: str, assigned_at: datetime) -> datetime:
        hours = self.config.sla_hours_by_priority.get(str(priority).upper(), self.config.sla_hours_by_priority["MEDIUM"])
        return assigned_at + timedelta(hours=hours)

    def calculate_sla_status(self, sla_due_at: datetime | str | None) -> str:
        due_at = self._parse_datetime(sla_due_at)
        if due_at is None:
            return SlaStatus.NOT_APPLICABLE.value
        now = datetime.now(UTC)
        if now > due_at:
            return SlaStatus.BREACHED.value
        remaining_seconds = (due_at - now).total_seconds()
        if remaining_seconds <= 2 * 60 * 60:
            return SlaStatus.AT_RISK.value
        return SlaStatus.ON_TRACK.value

    def refresh_case_sla_status(self, case: dict[str, Any]) -> dict[str, Any]:
        updated = dict(case)
        updated["sla_status"] = self.calculate_sla_status(updated.get("sla_due_at"))
        return updated

    def refresh_all_sla_statuses(self) -> dict[str, Any]:
        updated_count = 0
        for case in self.repository.list_cases():
            next_status = self.calculate_sla_status(case.get("sla_due_at"))
            if next_status != case.get("sla_status"):
                self.repository.update_case_assignment(case["case_id"], {"sla_status": next_status})
                updated_count += 1
        return {"updated_count": updated_count}

    @staticmethod
    def _parse_datetime(value: datetime | str | None) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=UTC)
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            return None
