import pytest

from app.core.constants import CaseStatus
from app.services.case_status_service import CaseStatusService
from app.services.errors import ApiError


def test_valid_status_transitions() -> None:
    service = CaseStatusService()

    assert service.is_transition_allowed("NEW", "AI_INVESTIGATION_IN_PROGRESS")
    assert service.is_transition_allowed("AI_INVESTIGATION_IN_PROGRESS", "AI_INVESTIGATION_COMPLETED")
    assert service.is_transition_allowed("AI_INVESTIGATION_COMPLETED", "PENDING_HUMAN_REVIEW")
    assert service.is_transition_allowed("PENDING_HUMAN_REVIEW", "HELD")
    assert service.is_transition_allowed("HELD", "CLOSED")


def test_invalid_new_to_closed_fails() -> None:
    service = CaseStatusService()

    with pytest.raises(ApiError):
        service.validate_transition("NEW", "CLOSED")


def test_closed_is_terminal() -> None:
    service = CaseStatusService()

    with pytest.raises(ApiError) as exc:
        service.validate_transition("CLOSED", "NEW")

    assert "already CLOSED" in exc.value.message


def test_unknown_status_fails() -> None:
    service = CaseStatusService()

    with pytest.raises(ApiError):
        service.validate_transition("UNKNOWN", "NEW")


def test_allowed_next_statuses() -> None:
    service = CaseStatusService()

    assert service.get_allowed_next_statuses(CaseStatus.PENDING_HUMAN_REVIEW.value) == [
        "APPROVED",
        "ESCALATED",
        "HELD",
        "REJECTED",
    ]
