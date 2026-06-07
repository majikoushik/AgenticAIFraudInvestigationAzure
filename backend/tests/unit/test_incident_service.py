from app.alerting.incident_repository import IncidentRepository
from app.alerting.incident_service import IncidentService
from app.alerting.json_file_store import JsonFileStore
from app.core.constants import AlertSeverity, AlertType, IncidentStatus


def _alert() -> dict:
    return {
        "alert_id": "ALERT-1",
        "alert_type": AlertType.HIGH_API_ERROR_RATE.value,
        "title": "High API error rate",
        "description": "Errors exceeded threshold.",
        "severity": AlertSeverity.SEV1_HIGH.value,
        "source": "test",
        "recommended_runbook": "docs/runbooks/high-api-error-rate.md",
    }


def test_incident_service_creates_and_updates_incident(tmp_path) -> None:
    service = IncidentService(IncidentRepository(JsonFileStore(str(tmp_path / "incidents.json"))))

    incident = service.create_incident_from_alert(_alert())
    updated = service.update_incident_status(incident["incident_id"], IncidentStatus.ACKNOWLEDGED.value, "ops-user")
    assigned = service.assign_incident(incident["incident_id"], "fraud-ops", "ops-user")

    assert incident["status"] == IncidentStatus.OPEN.value
    assert updated["acknowledged_by"] == "ops-user"
    assert assigned["assigned_to"] == "fraud-ops"


def test_incident_service_closes_incident(tmp_path) -> None:
    service = IncidentService(IncidentRepository(JsonFileStore(str(tmp_path / "incidents.json"))))
    incident = service.create_incident_from_alert(_alert())

    closed = service.close_incident(incident["incident_id"], "ops-user", "Issue resolved.")

    assert closed["status"] == IncidentStatus.CLOSED.value
    assert closed["closed_by"] == "ops-user"
