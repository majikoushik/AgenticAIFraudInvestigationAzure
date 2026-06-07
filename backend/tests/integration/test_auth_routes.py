from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_auth_mode_works_without_auth() -> None:
    response = client.get("/api/v1/auth/mode")

    assert response.status_code == 200
    assert response.json()["auth_mode"] == "local"


def test_auth_me_works_in_local_mode() -> None:
    response = client.get("/api/v1/auth/me", headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"})

    assert response.status_code == 200
    assert response.json()["user_id"] == "fraud_manager_01"
    assert response.json()["primary_role"] == "FRAUD_MANAGER"


def test_auth_permissions_returns_permissions() -> None:
    response = client.get("/api/v1/auth/permissions", headers={"X-Demo-Role": "AUDITOR"})

    assert response.status_code == 200
    assert "VIEW_AUDIT" in response.json()["permissions"]
