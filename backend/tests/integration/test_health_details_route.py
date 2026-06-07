from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_details_route_returns_safe_admin_payload() -> None:
    response = client.get("/api/v1/health/details", headers={"X-Demo-Role": "ADMIN"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "degraded", "unhealthy"}
    assert "checks" in payload
    assert "connection_string" not in response.text.lower()
