from app.alerting.alert_repository import AlertRepository
from app.alerting.alert_service import AlertService
from app.alerting.json_file_store import JsonFileStore
from app.core.constants import AlertSeverity, AlertType


class _IncidentService:
    def __init__(self) -> None:
        self.created = []

    def create_incident_from_alert(self, alert: dict) -> dict:
        self.created.append(alert)
        return {"incident_id": "INC-1", "alert_id": alert["alert_id"]}


def _alert_data() -> dict:
    return {
        "alert_type": AlertType.HIGH_API_ERROR_RATE.value,
        "severity": AlertSeverity.SEV1_HIGH.value,
        "title": "High API error rate",
        "description": "Errors exceeded threshold.",
        "source": "test",
        "metric_name": "api_error_rate_percentage",
        "metric_value": 50,
        "threshold_value": 5,
        "properties": {"customer_name": "Fake Person"},
    }


def test_alert_service_creates_alert_and_incident(tmp_path) -> None:
    incident_service = _IncidentService()
    repository = AlertRepository(JsonFileStore(str(tmp_path / "alerts.json")))
    service = AlertService(repository, incident_service)

    alert = service.create_alert(_alert_data())

    assert alert["status"] == "ACTIVE"
    assert alert["properties"]["customer_name"] == "***MASKED***"
    assert incident_service.created


def test_alert_service_deduplicates_active_alerts(tmp_path) -> None:
    repository = AlertRepository(JsonFileStore(str(tmp_path / "alerts.json")))
    service = AlertService(repository, _IncidentService())

    first = service.create_alert(_alert_data())
    second = service.create_alert(_alert_data())

    assert second["alert_id"] == first["alert_id"]
    assert len(repository.list_alerts()) == 1
