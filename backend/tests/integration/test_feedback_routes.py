from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_submit_feedback_search_case_and_analytics() -> None:
    response = client.post(
        "/api/v1/feedback",
        headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"},
        json={
            "case_id": "case-001",
            "target_type": "AI_RECOMMENDATION",
            "rating": "POOR",
            "issue_types": ["INCORRECT_RECOMMENDATION"],
            "severity": "HIGH",
            "comment": "The recommendation should escalate due to beneficiary risk.",
            "expected_recommendation": "ESCALATE",
            "actual_ai_recommendation": "HOLD"
        },
    )

    assert response.status_code == 200
    feedback_id = response.json()["feedback_id"]

    list_response = client.get("/api/v1/feedback?case_id=case-001", headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"})
    case_response = client.get("/api/v1/cases/case-001/feedback", headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"})
    analytics_response = client.get("/api/v1/feedback/analytics/summary", headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"})

    assert list_response.status_code == 200
    assert case_response.status_code == 200
    assert analytics_response.status_code == 200
    assert any(item["feedback_id"] == feedback_id for item in list_response.json()["feedback_records"])


def test_negative_short_comment_fails_and_admin_can_export() -> None:
    bad = client.post(
        "/api/v1/feedback",
        headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"},
        json={"case_id": "case-001", "target_type": "AI_RECOMMENDATION", "rating": "POOR", "issue_types": [], "severity": "HIGH", "comment": "short"},
    )
    assert bad.status_code == 400

    created = client.post(
        "/api/v1/feedback",
        headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"},
        json={"case_id": "case-001", "target_type": "POLICY_CITATION", "rating": "POOR", "issue_types": ["WRONG_POLICY_CITATION"], "severity": "HIGH", "comment": "Wrong policy citation was selected.", "policy_source_file": "fraud-investigation-policy.md"},
    )
    feedback_id = created.json()["feedback_id"]
    disposition = client.patch(f"/api/v1/feedback/{feedback_id}/disposition", headers={"X-Demo-User": "fraud_manager_01", "X-Demo-Role": "FRAUD_MANAGER"}, json={"disposition": "ACCEPTED_FOR_IMPROVEMENT"})
    export = client.post("/api/v1/feedback/export/eval-dataset", headers={"X-Demo-User": "admin_01", "X-Demo-Role": "ADMIN"})

    assert created.status_code == 200
    assert disposition.status_code == 200
    assert export.status_code == 200
