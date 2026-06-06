from datetime import UTC, datetime
from uuid import uuid4

from app.core.constants import AuditEventType, ReviewerRole
from app.schemas.audit_schema import AuditEvent


class AuditService:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record_event(
        self,
        case_id: str,
        event_type: AuditEventType,
        actor: str,
        actor_role: ReviewerRole,
        previous_status: str | None = None,
        new_status: str | None = None,
        decision: str | None = None,
        reason_code: str | None = None,
        comment: str | None = None,
        ai_recommendation: str | None = None,
        human_decision: str | None = None,
        human_override: bool = False,
        override_reason: str | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            audit_id=f"AUDIT-{uuid4().hex[:12].upper()}",
            case_id=case_id,
            event_type=event_type.value,
            actor=actor,
            actor_role=actor_role.value,
            previous_status=previous_status,
            new_status=new_status,
            decision=decision,
            reason_code=reason_code,
            comment=comment,
            ai_recommendation=ai_recommendation,
            human_decision=human_decision,
            human_override=human_override,
            override_reason=override_reason,
            timestamp=datetime.now(UTC).isoformat(),
        )
        self._events.append(event)
        return event

    def get_entries(self, case_id: str) -> list[AuditEvent]:
        return sorted(
            [event for event in self._events if event.case_id == case_id],
            key=lambda event: event.timestamp,
        )

    def clear_case(self, case_id: str) -> None:
        self._events = [event for event in self._events if event.case_id != case_id]


audit_service = AuditService()
