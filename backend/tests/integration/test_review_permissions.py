from fastapi.testclient import TestClient

from app.core.constants import CaseStatus
from app.main import app
from app.services.audit_service import audit_service
from app.services.case_service import CaseService
from app.services.case_status_service import case_status_service


client = TestClient(app)


def reset_case() -> None:
    case_status_service.force_status("case-001", CaseStatus.PENDING_HUMAN_REVIEW)
    audit_service.clear_case("case-001")
    CaseService._ai_recommendations["case-001"] = "APPROVE"


def payload(decision: str = "APPROVE") -> dict:
    return {
        "decision": decision,
        "comment": "Synthetic review comment with enough detail.",
        "reviewed_by": "ignored",
        "reviewer_role": "FRAUD_ANALYST",
        "reason_code": "CUSTOMER_CONFIRMED",
        "evidence_acknowledged": True,
        "policy_acknowledged": True,
    }


def test_review_rejects_fraud_analyst_approve() -> None:
    reset_case()

    response = client.post("/api/v1/cases/case-001/review", headers={"X-Demo-Role": "FRAUD_ANALYST"}, json=payload())

    assert response.status_code == 403


def test_review_rejects_auditor() -> None:
    reset_case()

    response = client.post("/api/v1/cases/case-001/review", headers={"X-Demo-Role": "AUDITOR"}, json=payload("HOLD"))

    assert response.status_code == 403


def test_review_allows_fraud_manager_approve() -> None:
    reset_case()

    response = client.post("/api/v1/cases/case-001/review", headers={"X-Demo-User": "manager_01", "X-Demo-Role": "FRAUD_MANAGER"}, json=payload())

    assert response.status_code == 200
    assert response.json()["reviewed_by"] == "manager_01"
    assert response.json()["reviewer_role"] == "FRAUD_MANAGER"
