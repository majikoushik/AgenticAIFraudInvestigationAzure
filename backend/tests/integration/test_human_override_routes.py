from fastapi.testclient import TestClient

from app.core.constants import CaseStatus
from app.main import app
from app.repositories.case_repository import CaseRepository
from app.services.audit_service import audit_service
from app.services.case_service import CaseService
from app.services.case_status_service import case_status_service


client = TestClient(app)
repository = CaseRepository()


def reset_case(case_id: str, status: CaseStatus = CaseStatus.PENDING_HUMAN_REVIEW, ai_recommendation: str | None = "HOLD") -> None:
    case_status_service.force_status(case_id, status)
    audit_service.clear_case(case_id)
    CaseService._ai_recommendations[case_id] = ai_recommendation
    CaseService._investigation_summaries.pop(case_id, None)
    repository.update_case_human_review(case_id, None)
    repository.update_case_override_summary(case_id, None)


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


def test_review_same_decision_does_not_create_override() -> None:
    reset_case("case-001", ai_recommendation="HOLD")

    response = client.post("/api/v1/cases/case-001/review", json=review_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["human_override"] is False
    assert payload["override_comparison_status"] == "MATCHED"


def test_review_different_decision_requires_override_reason() -> None:
    reset_case("case-001", ai_recommendation="HOLD")

    response = client.post("/api/v1/cases/case-001/review", json=review_payload(decision="ESCALATE"))

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "override_reason_required"


def test_review_different_decision_stores_summary_and_audit_event() -> None:
    reset_case("case-001", ai_recommendation="HOLD")

    response = client.post(
        "/api/v1/cases/case-001/review",
        json=review_payload(
            decision="ESCALATE",
            override_reason="Beneficiary linked to multiple suspicious synthetic cases.",
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["human_override"] is True
    assert payload["override_comparison_status"] == "OVERRIDDEN"
    assert payload["ai_recommendation"] == "HOLD"
    assert payload["human_decision"] == "ESCALATE"

    summary_response = client.get("/api/v1/cases/case-001/override-summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["has_override"] is True
    assert summary["ai_recommendation"] == "HOLD"
    assert summary["human_decision"] == "ESCALATE"

    audit_response = client.get("/api/v1/cases/case-001/audit")
    event_types = [event["event_type"] for event in audit_response.json()["events"]]
    assert "HUMAN_OVERRIDE_DETECTED" in event_types


def test_review_missing_ai_recommendation_does_not_create_override_event() -> None:
    reset_case("case-002", ai_recommendation=None)

    response = client.post("/api/v1/cases/case-002/review", json=review_payload())

    assert response.status_code == 200
    assert response.json()["human_override"] is False
    assert response.json()["override_comparison_status"] == "AI_RECOMMENDATION_MISSING"

    audit_response = client.get("/api/v1/cases/case-002/audit")
    events = audit_response.json()["events"]
    assert "HUMAN_OVERRIDE_DETECTED" not in [event["event_type"] for event in events]
    decision_events = [event for event in events if event["event_type"] == "HUMAN_DECISION_SUBMITTED"]
    assert decision_events[-1]["metadata"]["override_comparison_status"] == "AI_RECOMMENDATION_MISSING"


def test_case_response_includes_override_summary() -> None:
    reset_case("case-001", ai_recommendation="HOLD")
    client.post(
        "/api/v1/cases/case-001/review",
        json=review_payload(
            decision="ESCALATE",
            override_reason="Beneficiary linked to multiple suspicious synthetic cases.",
        ),
    )

    response = client.get("/api/v1/cases/case-001")

    assert response.status_code == 200
    assert response.json()["override_summary"]["has_override"] is True
