from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_my_queue_route_returns_current_user_cases() -> None:
    response = client.get(
        "/api/v1/queues/my",
        headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"},
    )

    assert response.status_code == 200
    assert response.json()["queue_name"] == "my_queue"


def test_unassigned_queue_requires_manager_permission() -> None:
    response = client.get(
        "/api/v1/queues/unassigned",
        headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"},
    )

    assert response.status_code == 403


def test_manager_can_view_unassigned_queue() -> None:
    response = client.get(
        "/api/v1/queues/unassigned",
        headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"},
    )

    assert response.status_code == 200
    assert response.json()["queue_name"] == "unassigned_queue"


def test_team_queue_returns_team_cases() -> None:
    response = client.get(
        "/api/v1/queues/team?team=Fraud%20Operations",
        headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"},
    )

    assert response.status_code == 200
    assert response.json()["queue_name"] == "team_queue"


def test_sla_risk_queue_route() -> None:
    response = client.get(
        "/api/v1/queues/sla-risk",
        headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"},
    )

    assert response.status_code == 200
    assert response.json()["queue_name"] == "sla_risk_queue"


def test_workload_route() -> None:
    response = client.get(
        "/api/v1/assignment/workload",
        headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"},
    )

    assert response.status_code == 200
    assert "active_cases_by_investigator" in response.json()
