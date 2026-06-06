from fastapi.testclient import TestClient

from app.core.constants import AuditEventType, ReviewerRole
from app.main import app
from app.services.audit_service import audit_service


client = TestClient(app)


def test_case_audit_returns_ordered_events() -> None:
    audit_service.clear_case("case-001")
    audit_service.record_event("case-001", AuditEventType.CASE_VIEWED, "system", ReviewerRole.SYSTEM)

    response = client.get("/api/v1/cases/case-001/audit")

    assert response.status_code == 200
    assert response.json()["count"] >= 1


def test_audit_event_types_endpoint() -> None:
    response = client.get("/api/v1/audit/event-types")

    assert response.status_code == 200
    assert any(item["event_type"] == "CASE_STATUS_CHANGED" for item in response.json()["event_types"])


def test_audit_search_filters_events() -> None:
    audit_service.clear_case("case-search")
    audit_service.record_event("case-search", AuditEventType.SECURITY_EVENT, "auditor", ReviewerRole.AUDITOR)

    response = client.get("/api/v1/audit/search", params={"case_id": "case-search", "actor_role": "AUDITOR"})

    assert response.status_code == 200
    assert response.json()["count"] == 1
