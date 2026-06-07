from app.alerting.alert_repository import AlertRepository
from app.alerting.json_file_store import JsonFileStore


def test_alert_repository_appends_sorts_and_filters(tmp_path) -> None:
    repository = AlertRepository(JsonFileStore(str(tmp_path / "alerts.json")))

    repository.append_alert({"alert_id": "a-old", "alert_type": "HIGH_API_LATENCY", "severity": "SEV2_MEDIUM", "status": "RESOLVED", "created_at": "2026-01-01T00:00:00Z"})
    repository.append_alert({"alert_id": "a-new", "alert_type": "HIGH_API_ERROR_RATE", "severity": "SEV1_HIGH", "status": "ACTIVE", "created_at": "2026-01-02T00:00:00Z"})

    assert repository.list_alerts()[0]["alert_id"] == "a-new"
    assert repository.get_alert_by_id("a-old")["status"] == "RESOLVED"
    assert repository.search_alerts(status="ACTIVE")[0]["alert_type"] == "HIGH_API_ERROR_RATE"


def test_alert_repository_resolves_alert(tmp_path) -> None:
    repository = AlertRepository(JsonFileStore(str(tmp_path / "alerts.json")))
    repository.append_alert({"alert_id": "a-1", "status": "ACTIVE", "created_at": "2026-01-01T00:00:00Z"})

    updated = repository.update_alert_status("a-1", "RESOLVED")

    assert updated["status"] == "RESOLVED"
    assert updated["resolved_at"]
