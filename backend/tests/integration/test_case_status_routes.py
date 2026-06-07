from fastapi.testclient import TestClient

from app.core.constants import CaseStatus
from app.main import app
from app.services.audit_service import audit_service
from app.services.case_status_service import case_status_service


client = TestClient(app)


def reset_case(case_id: str, status: CaseStatus) -> None:
    case_status_service.force_status(case_id, status)
    audit_service.clear_case(case_id)


def test_get_status_endpoint_returns_allowed_next_statuses() -> None:
    reset_case("case-001", CaseStatus.NEW)

    response = client.get("/api/v1/cases/case-001/status")

    assert response.status_code == 200
    assert response.json()["status"] == "NEW"
    assert response.json()["allowed_next_statuses"] == ["AI_INVESTIGATION_IN_PROGRESS"]


def test_patch_status_endpoint_validates_transition_and_creates_audit() -> None:
    reset_case("case-001", CaseStatus.NEW)

    response = client.patch(
        "/api/v1/cases/case-001/status",
        headers={"X-Demo-Role": "ADMIN"},
        json={
            "target_status": "AI_INVESTIGATION_IN_PROGRESS",
            "actor": "system",
            "actor_role": "SYSTEM",
            "comment": "AI investigation started",
        },
    )

    assert response.status_code == 200
    assert response.json()["new_status"] == "AI_INVESTIGATION_IN_PROGRESS"

    audit_response = client.get("/api/v1/cases/case-001/audit")
    assert audit_response.status_code == 200
    assert audit_response.json()["events"][0]["event_type"] == "AI_INVESTIGATION_STARTED"


def test_patch_status_endpoint_rejects_invalid_transition() -> None:
    reset_case("case-001", CaseStatus.NEW)

    response = client.patch(
        "/api/v1/cases/case-001/status",
        headers={"X-Demo-Role": "ADMIN"},
        json={
            "target_status": "CLOSED",
            "actor": "system",
            "actor_role": "SYSTEM",
            "comment": "Invalid transition",
        },
    )

    assert response.status_code == 400
    assert "Invalid status transition" in response.json()["error"]["message"]
