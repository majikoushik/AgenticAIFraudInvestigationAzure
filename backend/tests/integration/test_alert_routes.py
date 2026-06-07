import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.constants import AlertSeverity, AlertType
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
def clear_alerting_stores():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "[]" for path in LOCAL_STORES}
    for path in LOCAL_STORES:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[]", encoding="utf-8")
    yield
    for path, content in originals.items():
        path.write_text(content, encoding="utf-8")


def _simulate_alert() -> dict:
    response = client.post(
        "/api/v1/alerts/simulate",
        headers=ADMIN_HEADERS,
        json={
            "alert_type": AlertType.HIGH_API_ERROR_RATE.value,
            "severity": AlertSeverity.SEV1_HIGH.value,
            "title": "Simulated API error alert",
            "description": "Synthetic alert for integration tests.",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_alert_routes_simulate_list_get_and_resolve_alert() -> None:
    simulated = _simulate_alert()
    alert_id = simulated["alert"]["alert_id"]

    list_response = client.get("/api/v1/alerts", headers=ADMIN_HEADERS)
    get_response = client.get(f"/api/v1/alerts/{alert_id}", headers=ADMIN_HEADERS)
    resolve_response = client.post(f"/api/v1/alerts/{alert_id}/resolve", headers=ADMIN_HEADERS, json={"actor": "admin_user", "comment": "Resolved in test."})

    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    assert get_response.status_code == 200
    assert get_response.json()["alert_id"] == alert_id
    assert resolve_response.status_code == 200
    assert resolve_response.json()["status"] == "RESOLVED"


def test_alert_route_requires_admin_permission() -> None:
    response = client.get("/api/v1/alerts", headers={"X-Demo-Role": "AUDITOR"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "permission_denied"


def test_alert_route_returns_404_for_missing_alert() -> None:
    response = client.get("/api/v1/alerts/ALERT-MISSING", headers=ADMIN_HEADERS)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "alert_not_found"
