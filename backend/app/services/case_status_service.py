from app.core.constants import ALLOWED_STATUS_TRANSITIONS, CaseStatus
from app.services.errors import ApiError


class CaseStatusService:
    def __init__(self) -> None:
        self._statuses: dict[str, CaseStatus] = {}

    def get_status(self, case_id: str, initial_status: str | None = None) -> CaseStatus:
        if case_id not in self._statuses:
            self._statuses[case_id] = self._normalize_status(initial_status)
        return self._statuses[case_id]

    def set_initial_status(self, case_id: str, initial_status: str | None) -> None:
        self._statuses.setdefault(case_id, self._normalize_status(initial_status))

    def transition(self, case_id: str, current_status: CaseStatus, new_status: CaseStatus) -> tuple[CaseStatus, CaseStatus]:
        allowed_targets = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())
        if new_status not in allowed_targets:
            raise ApiError(
                400,
                "invalid_status_transition",
                f"Invalid status transition from {current_status.value} to {new_status.value}.",
            )
        self._statuses[case_id] = new_status
        return current_status, new_status

    def force_status(self, case_id: str, new_status: CaseStatus) -> None:
        self._statuses[case_id] = new_status

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


case_status_service = CaseStatusService()
