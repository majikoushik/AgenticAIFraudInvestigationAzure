from app.core.constants import AuditEventType, ReviewerRole
from app.repositories.audit_repository import AuditRepository
from app.services.audit_service import AuditService


def service(tmp_path) -> AuditService:
    return AuditService(AuditRepository(tmp_path / "audit_events.json"))


def test_audit_service_generates_audit_id_and_category(tmp_path) -> None:
    audit_service = service(tmp_path)

    event = audit_service.create_status_change_event("case-001", "NEW", "AI_INVESTIGATION_IN_PROGRESS")

    assert event.audit_id.startswith("AUDIT-")
    assert event.event_category == "CASE"


def test_human_decision_helper_creates_event(tmp_path) -> None:
    event = service(tmp_path).create_human_decision_event(
        case_id="case-001",
        actor="reviewer",
        actor_role=ReviewerRole.FRAUD_ANALYST,
        decision="HOLD",
        reason_code="SUSPICIOUS_DEVICE",
        ai_recommendation="HOLD",
        human_override=False,
    )

    assert event.event_type == AuditEventType.HUMAN_DECISION_SUBMITTED
    assert event.event_category == "HUMAN_REVIEW"


def test_human_override_helper_creates_event(tmp_path) -> None:
    event = service(tmp_path).create_human_override_event(
        "case-001",
        "manager",
        ReviewerRole.FRAUD_MANAGER,
        "HOLD",
        "ESCALATE",
        "Synthetic override reason.",
    )

    assert event.human_override is True


def test_rag_and_agent_helpers_create_events(tmp_path) -> None:
    audit_service = service(tmp_path)

    rag_event = audit_service.create_rag_retrieval_event("case-001", AuditEventType.RAG_RETRIEVAL_COMPLETED, "policy", ["policy.md"])
    agent_event = audit_service.create_agent_execution_event("case-001", AuditEventType.AGENT_EXECUTION_COMPLETED, "PolicyRagAgent")

    assert rag_event.event_category == "RAG"
    assert agent_event.event_category == "AGENT"
