import pytest

from app.core.constants import OverrideComparisonStatus
from app.services.errors import ApiError
from app.services.human_override_service import HumanOverrideService


def test_compare_decisions_returns_matched_for_same_values() -> None:
    result = HumanOverrideService().compare_decisions("HOLD", "HOLD")

    assert result["human_override"] is False
    assert result["override_comparison_status"] == OverrideComparisonStatus.MATCHED.value


def test_compare_decisions_returns_overridden_for_different_values() -> None:
    result = HumanOverrideService().compare_decisions("HOLD", "ESCALATE")

    assert result["human_override"] is True
    assert result["override_comparison_status"] == OverrideComparisonStatus.OVERRIDDEN.value


def test_compare_decisions_normalizes_lowercase_and_legacy_values() -> None:
    result = HumanOverrideService().compare_decisions("held", "hold")

    assert result["ai_recommendation"] == "HOLD"
    assert result["human_decision"] == "HOLD"
    assert result["override_comparison_status"] == OverrideComparisonStatus.MATCHED.value


def test_compare_decisions_handles_missing_ai_recommendation() -> None:
    result = HumanOverrideService().compare_decisions(None, "HOLD")

    assert result["human_override"] is False
    assert result["override_comparison_status"] == OverrideComparisonStatus.AI_RECOMMENDATION_MISSING.value


def test_validate_override_reason_passes_for_valid_reason() -> None:
    HumanOverrideService().validate_override_reason(True, "Valid synthetic override reason.")


def test_validate_override_reason_fails_when_missing() -> None:
    with pytest.raises(ApiError) as exc:
        HumanOverrideService().validate_override_reason(True, None)

    assert exc.value.code == "override_reason_required"


def test_validate_override_reason_fails_when_too_short() -> None:
    with pytest.raises(ApiError) as exc:
        HumanOverrideService().validate_override_reason(True, "short")

    assert exc.value.code == "override_reason_too_short"
