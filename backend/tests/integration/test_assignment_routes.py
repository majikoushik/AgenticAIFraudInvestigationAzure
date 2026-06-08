from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_manager_can_assign_case_route() -> None:
    response = client.post(
        "/api/v1/cases/case-001/assign",
        headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"},
        json={
            "assigned_to": "fraud_analyst_01",
            "assigned_to_name": "Fraud Analyst 01",
            "assigned_to_role": "FRAUD_ANALYST",
            "assigned_team": "Fraud Operations",
            "assignment_priority": "HIGH",
            "comment": "Synthetic integration assignment."
        },
    )

    assert response.status_code == 200
    assert response.json()["assignment"]["assigned_to"] == "fraud_analyst_01"


def test_assigned_user_can_accept_case_route() -> None:
    response = client.post(
        "/api/v1/cases/case-002/accept",
        headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"},
        json={"accepted_by": "fraud_analyst_01", "comment": "Accepted for test."},
    )

    assert response.status_code == 200
    assert response.json()["assignment"]["assignment_status"] == "ACCEPTED"


def test_auditor_cannot_assign_case_route() -> None:
    response = client.post(
        "/api/v1/cases/case-007/assign",
        headers={"X-Demo-User": "auditor_01", "X-Demo-Role": "AUDITOR"},
        json={
            "assigned_to": "fraud_analyst_02",
            "assigned_to_name": "Fraud Analyst 02",
            "assigned_to_role": "FRAUD_ANALYST",
            "assigned_team": "Fraud Operations",
            "assignment_priority": "MEDIUM"
        },
    )

    assert response.status_code == 403


def test_closed_case_cannot_be_assigned_route() -> None:
    response = client.post(
        "/api/v1/cases/case-006/assign",
        headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"},
        json={
            "assigned_to": "fraud_analyst_01",
            "assigned_to_name": "Fraud Analyst 01",
            "assigned_to_role": "FRAUD_ANALYST",
            "assigned_team": "Fraud Operations",
            "assignment_priority": "LOW"
        },
    )

    assert response.status_code == 400


def test_assignment_history_route() -> None:
    response = client.get(
        "/api/v1/cases/case-001/assignment-history",
        headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"},
    )

    assert response.status_code == 200
    assert response.json()["case_id"] == "case-001"
