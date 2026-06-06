from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.core.constants import AUDIT_EVENT_CATEGORY_BY_TYPE, AuditEventType, ReviewerRole


class AuditEventCreate(BaseModel):
    case_id: str | None = None
    event_type: AuditEventType
    event_category: str | None = None
    actor: str = "system"
    actor_role: ReviewerRole = ReviewerRole.SYSTEM
    action: str
    description: str
    previous_status: str | None = None
    new_status: str | None = None
    decision: str | None = None
    reason_code: str | None = None
    ai_recommendation: str | None = None
    human_decision: str | None = None
    human_override: bool = False
    override_reason: str | None = None
    agent_name: str | None = None
    tool_name: str | None = None
    rag_query: str | None = None
    rag_sources: list[str] = Field(default_factory=list)
    error_code: str | None = None
    error_message: str | None = None
    correlation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime | None = None

    @model_validator(mode="after")
    def derive_category(self) -> "AuditEventCreate":
        self.event_category = self.event_category or AUDIT_EVENT_CATEGORY_BY_TYPE[self.event_type]
        return self


class AuditEventResponse(AuditEventCreate):
    audit_id: str
    timestamp: datetime


class AuditEventListResponse(BaseModel):
    case_id: str | None = None
    count: int
    events: list[AuditEventResponse]


class AuditSearchQuery(BaseModel):
    case_id: str | None = None
    event_type: str | None = None
    actor: str | None = None
    actor_role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
