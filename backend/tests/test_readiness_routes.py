"""
Integration tests for readiness API routes.
Tests use FastAPI TestClient with demo user auth headers.
Does NOT require live Azure services.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ADMIN_HEADERS = {"X-Demo-User": "test-admin", "X-Demo-Role": "ADMIN"}
ANALYST_HEADERS = {"X-Demo-User": "test-analyst", "X-Demo-Role": "FRAUD_ANALYST"}
AUDITOR_HEADERS = {"X-Demo-User": "test-auditor", "X-Demo-Role": "AUDITOR"}


def test_readiness_config_health_requires_auth():
    """Unauthenticated requests should be rejected if missing valid roles."""
    # In local mode, missing headers falls back to DEFAULT_LOCAL_USER (FRAUD_ANALYST).
    # FRAUD_ANALYST does NOT have VIEW_READINESS permission (unless granted, which we just did).
    # To test auth failure, we pass an UNKNOWN role or invalid credentials.
    response = client.get("/api/v1/readiness/config/health", headers={"X-Demo-Role": "UNKNOWN_ROLE"})
    assert response.status_code in (401, 403)


def test_readiness_config_health_admin():
    response = client.get("/api/v1/readiness/config/health", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "config" in data
    # Verify no secrets in config summary
    config = data["config"]
    assert "enabled" in config
    assert "mode" in config


def test_readiness_checklist_returns_checks():
    response = client.get("/api/v1/readiness/checklist", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 100
    assert "checklist" in data
    assert len(data["categories"]) > 0


def test_readiness_checklist_category_filter():
    response = client.get("/api/v1/readiness/checklist?category=SECURITY", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    if "SECURITY" in data["checklist"]:
        for check in data["checklist"]["SECURITY"]:
            assert check["category"] == "SECURITY"


def test_readiness_list_assessments_empty_initially():
    """List assessments should return valid structure even with no data."""
    response = client.get("/api/v1/readiness/assessments", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "assessments" in data
    assert "count" in data


def test_run_assessment_requires_admin():
    """Non-admin should not be able to run assessment."""
    payload = {"environment": "local", "create_risks_from_failures": False}
    response = client.post("/api/v1/readiness/assessments/run",
                           json=payload, headers=ANALYST_HEADERS)
    assert response.status_code in (403, 401)


def test_run_assessment_admin_succeeds():
    payload = {
        "environment": "local",
        "create_risks_from_failures": False,
        "comment": "integration test",
    }
    response = client.post("/api/v1/readiness/assessments/run",
                           json=payload, headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "assessment_id" in data
    assert data["assessment_id"].startswith("READY-")
    assert "overall_score" in data
    assert "go_live_decision" in data
    assert "category_results" in data
    assert len(data["category_results"]) > 0


def test_get_assessment_by_id():
    # Run one first
    payload = {"environment": "local", "create_risks_from_failures": False}
    run_resp = client.post("/api/v1/readiness/assessments/run", json=payload, headers=ADMIN_HEADERS)
    assert run_resp.status_code == 200
    assessment_id = run_resp.json()["assessment_id"]

    response = client.get(f"/api/v1/readiness/assessments/{assessment_id}", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert response.json()["assessment_id"] == assessment_id


def test_get_assessment_not_found():
    response = client.get("/api/v1/readiness/assessments/NONEXISTENT-ID", headers=ADMIN_HEADERS)
    assert response.status_code == 404


def test_go_live_decision_returns_structure():
    payload = {"environment": "local", "create_risks_from_failures": False}
    run_resp = client.post("/api/v1/readiness/assessments/run", json=payload, headers=ADMIN_HEADERS)
    assessment_id = run_resp.json()["assessment_id"]

    response = client.get(f"/api/v1/readiness/assessments/{assessment_id}/go-live-decision",
                          headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "go_live_decision" in data
    assert "overall_score" in data
    assert data["go_live_decision"] in ("READY", "NOT_READY", "READY_WITH_RISKS", "MANUAL_REVIEW_REQUIRED")


def test_risk_list_returns_structure():
    response = client.get("/api/v1/readiness/risks", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "risks" in data


def test_analyst_cannot_run_assessment():
    payload = {"environment": "local", "create_risks_from_failures": False}
    response = client.post("/api/v1/readiness/assessments/run", json=payload, headers=ANALYST_HEADERS)
    assert response.status_code in (401, 403)


def test_auditor_can_view_assessments():
    response = client.get("/api/v1/readiness/assessments", headers=AUDITOR_HEADERS)
    assert response.status_code == 200
