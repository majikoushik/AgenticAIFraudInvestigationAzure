from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_metrics_summary_endpoint_returns_all_groups() -> None:
    response = client.get("/api/v1/metrics/summary")

    assert response.status_code == 200
    payload = response.json()
    assert "case_status_metrics" in payload
    assert "ai_recommendation_metrics" in payload
    assert "audit_metrics" in payload


def test_case_status_metrics_endpoint() -> None:
    response = client.get("/api/v1/metrics/case-status")

    assert response.status_code == 200
    assert "status_counts" in response.json()


def test_ai_vs_human_metrics_endpoint() -> None:
    response = client.get("/api/v1/metrics/ai-vs-human")

    assert response.status_code == 200
    assert "override_pairs" in response.json()


def test_operations_metrics_endpoint() -> None:
    response = client.get("/api/v1/metrics/operations")

    assert response.status_code == 200
    assert "agent_execution_metrics" in response.json()
    assert "rag_retrieval_metrics" in response.json()


def test_audit_metrics_endpoint() -> None:
    response = client.get("/api/v1/metrics/audit")

    assert response.status_code == 200
    assert "audit_events_by_type" in response.json()


def test_timeseries_metrics_endpoint() -> None:
    response = client.get("/api/v1/metrics/timeseries")

    assert response.status_code == 200
    assert "cases_created_by_date" in response.json()
