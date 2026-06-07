from app.alerting.incident_repository import IncidentRepository
from app.alerting.json_file_store import JsonFileStore


def test_incident_repository_appends_sorts_filters_and_updates(tmp_path) -> None:
    repository = IncidentRepository(JsonFileStore(str(tmp_path / "incidents.json")))

    repository.append_incident({"incident_id": "i-old", "severity": "SEV2_MEDIUM", "status": "OPEN", "assigned_to": "ops-a", "created_at": "2026-01-01T00:00:00Z"})
    repository.append_incident({"incident_id": "i-new", "severity": "SEV1_HIGH", "status": "ACKNOWLEDGED", "assigned_to": "ops-b", "created_at": "2026-01-02T00:00:00Z"})

    assert repository.list_incidents()[0]["incident_id"] == "i-new"
    assert repository.search_incidents(severity="SEV1_HIGH")[0]["assigned_to"] == "ops-b"
    assert repository.update_incident("i-old", {"status": "RESOLVED"})["status"] == "RESOLVED"
