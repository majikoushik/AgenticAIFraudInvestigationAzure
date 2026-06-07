from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.constants import AlertSeverity, AlertType, IncidentStatus
from app.main import app


client = TestClient(app)
ADMIN_HEADERS = {"X-Demo-User": "admin_user", "X-Demo-Role": "ADMIN"}
ROOT = Path(__file__).resolve().parents[3]
LOCAL_STORES = [
    ROOT / "data" / "synthetic" / "alerts.json",
    ROOT / "data" / "synthetic" / "incidents.json",
    ROOT / "data" / "synthetic" / "notifications.json",
]


@pytest.fixture(autouse=True)
def clear_incident_stores():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "[]" for path in LOCAL_STORES}
    for path in LOCAL_STORES:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[]", encoding="utf-8")
    yield
    for path, content in originals.items():
        path.write_text(content, encoding="utf-8")


def _create_incident() -> dict:
    response = client.post(
        "/api/v1/alerts/simulate",
        headers=ADMIN_HEADERS,
        json={
            "alert_type": AlertType.HIGH_AGENT_FAILURE_RATE.value,
            "severity": AlertSeverity.SEV1_HIGH.value,
            "title": "Simulated agent failure",
            "description": "Synthetic incident for integration tests.",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["incident"]


def test_incident_routes_list_get_update_assign_timeline_and_close() -> None:
    incident = _create_incident()
    incident_id = incident["incident_id"]

    list_response = client.get("/api/v1/incidents", headers=ADMIN_HEADERS)
    get_response = client.get(f"/api/v1/incidents/{incident_id}", headers=ADMIN_HEADERS)
    status_response = client.patch(f"/api/v1/incidents/{incident_id}/status", headers=ADMIN_HEADERS, json={"target_status": IncidentStatus.ACKNOWLEDGED.value, "actor": "admin_user"})
    assign_response = client.patch(f"/api/v1/incidents/{incident_id}/assign", headers=ADMIN_HEADERS, json={"assigned_to": "fraud-ops", "actor": "admin_user"})
    timeline_response = client.post(f"/api/v1/incidents/{incident_id}/timeline", headers=ADMIN_HEADERS, json={"actor": "admin_user", "action": "TRIAGE_NOTE", "comment": "Reviewed telemetry."})
    close_response = client.post(f"/api/v1/incidents/{incident_id}/close", headers=ADMIN_HEADERS, json={"actor": "admin_user", "comment": "Closed after mitigation."})

    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    assert get_response.status_code == 200
    assert status_response.json()["status"] == IncidentStatus.ACKNOWLEDGED.value
    assert assign_response.json()["assigned_to"] == "fraud-ops"
    assert timeline_response.json()["timeline"][-1]["action"] == "TRIAGE_NOTE"
    assert close_response.json()["status"] == IncidentStatus.CLOSED.value


def test_incident_route_rejects_invalid_status_transition() -> None:
    incident = _create_incident()

    response = client.patch(f"/api/v1/incidents/{incident['incident_id']}/status", headers=ADMIN_HEADERS, json={"target_status": IncidentStatus.CLOSED.value, "actor": "admin_user"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_incident_status_transition"


def test_incident_route_returns_404_for_missing_incident() -> None:
    response = client.get("/api/v1/incidents/INC-MISSING", headers=ADMIN_HEADERS)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "incident_not_found"
