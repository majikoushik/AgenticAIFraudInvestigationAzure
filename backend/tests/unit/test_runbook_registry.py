from app.alerting.runbook_registry import get_runbook_for_alert
from app.core.constants import AlertType


def test_runbook_registry_returns_specific_runbook() -> None:
    assert get_runbook_for_alert(AlertType.HIGH_API_ERROR_RATE.value) == "docs/runbooks/high-api-error-rate.md"


def test_runbook_registry_returns_general_runbook_for_unknown_type() -> None:
    assert get_runbook_for_alert("UNKNOWN_ALERT") == "docs/runbooks/general-incident-response.md"
