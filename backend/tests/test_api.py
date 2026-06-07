from fastapi.testclient import TestClient

from app.core.constants import CaseStatus
from app.main import app
from app.services.audit_service import audit_service
from app.services.case_service import CaseService
from app.services.case_status_service import case_status_service


client = TestClient(app)


def reset_case(case_id: str, status: CaseStatus = CaseStatus.PENDING_HUMAN_REVIEW, ai_recommendation: str | None = "HOLD") -> None:
    case_status_service.force_status(case_id, status)
    audit_service.clear_case(case_id)
    CaseService._ai_recommendations[case_id] = ai_recommendation
    CaseService._investigation_summaries.pop(case_id, None)


def review_payload(**overrides):
    payload = {
        "decision": "HOLD",
        "comment": "Synthetic review comment with enough detail.",
        "reviewed_by": "synthetic.reviewer",
        "reviewer_role": "FRAUD_ANALYST",
        "reason_code": "SUSPICIOUS_DEVICE",
        "evidence_acknowledged": True,
        "policy_acknowledged": True,
    }
    payload.update(overrides)
    return payload


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "fraud-investigation-backend",
    }


def test_get_case_list() -> None:
    response = client.get("/api/v1/cases")

    assert response.status_code == 200
    cases = response.json()
    assert len(cases) >= 3
    assert cases[0]["case_id"] == "case-001"


def test_get_case_details() -> None:
    reset_case("case-001")
    response = client.get("/api/v1/cases/case-001")

    assert response.status_code == 200
    case_detail = response.json()
    assert case_detail["metadata"]["case_id"] == "case-001"
    assert case_detail["customer"]["account_number_masked"] == "****3456"
    assert case_detail["suspicious_transaction"]["transaction_id"] == "txn-001"
    assert case_detail["current_status"] == "PENDING_HUMAN_REVIEW"


def test_investigate_case_returns_agent_package_and_sets_pending_review() -> None:
    reset_case("case-002", CaseStatus.NEW, None)
    response = client.post("/api/v1/cases/case-002/investigate")

    assert response.status_code == 200
    package = response.json()
    assert package["case_id"] == "case-002"
    assert package["investigation_summary"]["recommended_action"] == "escalate"

    detail_response = client.get("/api/v1/cases/case-002")
    assert detail_response.json()["current_status"] == "PENDING_HUMAN_REVIEW"
    audit_response = client.get("/api/v1/cases/case-002/audit")
    event_types = [event["event_type"] for event in audit_response.json()["events"]]
    assert "AI_INVESTIGATION_STARTED" in event_types
    assert "AI_INVESTIGATION_COMPLETED" in event_types


def test_submit_review_successfully_as_fraud_analyst_with_hold() -> None:
    reset_case("case-001")
    response = client.post("/api/v1/cases/case-001/review", json=review_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["new_status"] == "HELD"
    assert payload["human_override"] is False


def test_submit_review_successfully_as_fraud_manager_with_approve() -> None:
    reset_case("case-001", ai_recommendation="APPROVE")
    response = client.post(
        "/api/v1/cases/case-001/review",
        headers={"X-Demo-User": "synthetic.manager", "X-Demo-Role": "FRAUD_MANAGER"},
        json=review_payload(
            decision="APPROVE",
            reviewer_role="FRAUD_MANAGER",
            reason_code="CUSTOMER_CONFIRMED",
        ),
    )

    assert response.status_code == 200
    assert response.json()["new_status"] == "APPROVED"


def test_reject_auditor_decision_submission_with_403() -> None:
    reset_case("case-001")
    response = client.post(
        "/api/v1/cases/case-001/review",
        headers={"X-Demo-Role": "AUDITOR"},
        json=review_payload(reviewer_role="AUDITOR"),
    )

    assert response.status_code == 403


def test_reject_fraud_analyst_trying_to_approve_with_403() -> None:
    reset_case("case-001")
    response = client.post(
        "/api/v1/cases/case-001/review",
        json=review_payload(decision="APPROVE"),
    )

    assert response.status_code == 403


def test_reject_review_when_case_is_not_pending_human_review() -> None:
    reset_case("case-001", CaseStatus.NEW)
    response = client.post("/api/v1/cases/case-001/review", json=review_payload())

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "case_not_pending_review"


def test_reject_missing_evidence_acknowledgement() -> None:
    reset_case("case-001")
    response = client.post(
        "/api/v1/cases/case-001/review",
        json=review_payload(evidence_acknowledged=False),
    )

    assert response.status_code == 400


def test_reject_missing_policy_acknowledgement() -> None:
    reset_case("case-001")
    response = client.post(
        "/api/v1/cases/case-001/review",
        json=review_payload(policy_acknowledged=False),
    )

    assert response.status_code == 400


def test_reject_missing_override_reason_when_decision_differs_from_ai() -> None:
    reset_case("case-001", ai_recommendation="HOLD")
    response = client.post(
        "/api/v1/cases/case-001/review",
        json=review_payload(decision="ESCALATE"),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "override_reason_required"


def test_create_audit_and_override_events_after_human_review() -> None:
    reset_case("case-001", ai_recommendation="HOLD")
    response = client.post(
        "/api/v1/cases/case-001/review",
        json=review_payload(
            decision="ESCALATE",
            override_reason="Beneficiary linked to multiple suspicious synthetic cases.",
        ),
    )

    assert response.status_code == 200
    audit_response = client.get("/api/v1/cases/case-001/audit")
    event_types = [event["event_type"] for event in audit_response.json()["events"]]
    assert "HUMAN_DECISION_SUBMITTED" in event_types
    assert "HUMAN_OVERRIDE_DETECTED" in event_types


def test_close_case_successfully_as_fraud_manager() -> None:
    reset_case("case-001", CaseStatus.HELD)
    response = client.post(
        "/api/v1/cases/case-001/close",
        headers={"X-Demo-User": "synthetic.manager", "X-Demo-Role": "FRAUD_MANAGER"},
        json={
            "closed_by": "synthetic.manager",
            "closer_role": "FRAUD_MANAGER",
            "comment": "Closing after synthetic review.",
        },
    )

    assert response.status_code == 200
    assert response.json()["new_status"] == "CLOSED"


def test_reject_close_case_when_status_is_not_eligible() -> None:
    reset_case("case-001", CaseStatus.PENDING_HUMAN_REVIEW)
    response = client.post(
        "/api/v1/cases/case-001/close",
        headers={"X-Demo-User": "synthetic.manager", "X-Demo-Role": "FRAUD_MANAGER"},
        json={
            "closed_by": "synthetic.manager",
            "closer_role": "FRAUD_MANAGER",
            "comment": "Attempting close too early.",
        },
    )

    assert response.status_code == 400


def test_validate_status_transition_rules() -> None:
    reset_case("case-001", CaseStatus.NEW)
    response = client.post(
        "/api/v1/cases/case-001/close",
        headers={"X-Demo-User": "synthetic.manager", "X-Demo-Role": "FRAUD_MANAGER"},
        json={
            "closed_by": "synthetic.manager",
            "closer_role": "FRAUD_MANAGER",
            "comment": "Invalid close transition.",
        },
    )

    assert response.status_code == 400


def test_review_options() -> None:
    response = client.get("/api/v1/cases/case-001/review-options", params={"reviewer_role": "FRAUD_ANALYST"})

    assert response.status_code == 200
    assert response.json()["allowed_decisions"] == ["ESCALATE", "HOLD", "REJECT"]


def test_policy_search_endpoint_uses_local_fallback() -> None:
    response = client.get("/api/v1/rag/policies/search", params={"query": "new beneficiary review"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieval_mode"] in {"local", "azure_search"}
    assert payload["results"]


def test_agent_config_endpoint_does_not_expose_secrets() -> None:
    response = client.get("/api/v1/agents/config", headers={"X-Demo-Role": "ADMIN"})

    assert response.status_code == 200
    assert "api_key" not in response.text.lower()


def test_case_not_found() -> None:
    response = client.get("/api/v1/cases/case-missing")

    assert response.status_code == 404
