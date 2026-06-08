from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_security_health_requires_admin() -> None:
    denied = client.get("/api/v1/security/health", headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"})
    allowed = client.get("/api/v1/security/health", headers={"X-Demo-User": "admin_01", "X-Demo-Role": "ADMIN"})
    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert "secret" not in str(allowed.json()).lower() or "required_secrets" in allowed.json()
