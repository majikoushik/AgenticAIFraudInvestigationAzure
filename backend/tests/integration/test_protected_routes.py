from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_cases_endpoint_works_in_local_mode() -> None:
    response = client.get("/api/v1/cases", headers={"X-Demo-Role": "FRAUD_ANALYST"})

    assert response.status_code == 200


def test_metrics_endpoint_allows_auditor() -> None:
    response = client.get("/api/v1/metrics/summary", headers={"X-Demo-Role": "AUDITOR"})

    assert response.status_code == 200


def test_admin_config_rejects_non_admin() -> None:
    response = client.get("/api/v1/agents/config", headers={"X-Demo-Role": "FRAUD_ANALYST"})

    assert response.status_code == 403


def test_admin_config_allows_admin() -> None:
    response = client.get("/api/v1/agents/config", headers={"X-Demo-Role": "ADMIN"})

    assert response.status_code == 200


def test_status_patch_rejects_non_admin() -> None:
    response = client.patch(
        "/api/v1/cases/case-001/status",
        headers={"X-Demo-Role": "FRAUD_MANAGER"},
        json={"target_status": "AI_INVESTIGATION_IN_PROGRESS", "actor": "x", "actor_role": "SYSTEM"},
    )

    assert response.status_code == 403
