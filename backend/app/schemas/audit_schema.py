from pydantic import BaseModel


class AuditEvent(BaseModel):
    audit_id: str
    case_id: str
    event_type: str
    actor: str
    actor_role: str
    previous_status: str | None = None
    new_status: str | None = None
    decision: str | None = None
    reason_code: str | None = None
    comment: str | None = None
    ai_recommendation: str | None = None
    human_decision: str | None = None
    human_override: bool = False
    override_reason: str | None = None
    timestamp: str


class AuditTrailResponse(BaseModel):
    case_id: str
    events: list[AuditEvent]
