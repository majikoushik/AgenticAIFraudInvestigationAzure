from datetime import UTC, datetime
from uuid import uuid4

from app.core.constants import AUDIT_EVENT_CATEGORY_BY_TYPE, AuditEventType, ReviewerRole
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit_schema import AuditEventCreate, AuditEventListResponse, AuditEventResponse
from app.utils.audit_sanitizer import sanitize_audit_metadata


class AuditService:
    def __init__(self, repository: AuditRepository | None = None) -> None:
        self.repository = repository or AuditRepository()

    def create_event(self, event: AuditEventCreate) -> AuditEventResponse:
        timestamp = event.timestamp or datetime.now(UTC)
        response = AuditEventResponse(
            **event.model_dump(exclude={"timestamp", "metadata", "event_category"}),
            audit_id=self._generate_audit_id(timestamp),
            timestamp=timestamp,
            event_category=event.event_category or AUDIT_EVENT_CATEGORY_BY_TYPE[event.event_type],
            metadata=sanitize_audit_metadata(event.metadata),
        )
        self.repository.append_event(response.model_dump(mode="json"))
        return response

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
        metadata: dict | None = None,
    ) -> AuditEventResponse:
        return self.create_event(
            AuditEventCreate(
                case_id=case_id,
                event_type=event_type,
                actor=actor,
                actor_role=actor_role,
                action=self._default_action(event_type),
                description=self._default_description(event_type, previous_status, new_status, comment),
                previous_status=previous_status,
                new_status=new_status,
                decision=decision,
                reason_code=reason_code,
                comment=comment,
                ai_recommendation=ai_recommendation,
                human_decision=human_decision,
                human_override=human_override,
                override_reason=override_reason,
                metadata=metadata or {},
            )
        )

    def create_status_change_event(
        self,
        case_id: str,
        previous_status: str,
        new_status: str,
        actor: str = "system",
        actor_role: ReviewerRole = ReviewerRole.SYSTEM,
        comment: str | None = None,
    ) -> AuditEventResponse:
        event_type = AuditEventType.CASE_CLOSED if new_status == "CLOSED" else AuditEventType.CASE_STATUS_CHANGED
        return self.record_event(case_id, event_type, actor, actor_role, previous_status, new_status, comment=comment)

    def create_ai_investigation_event(
        self,
        case_id: str,
        event_type: AuditEventType,
        metadata: dict | None = None,
        comment: str | None = None,
    ) -> AuditEventResponse:
        return self.record_event(
            case_id=case_id,
            event_type=event_type,
            actor="system",
            actor_role=ReviewerRole.SYSTEM,
            comment=comment,
            metadata=metadata or {},
        )

    def create_agent_execution_event(
        self,
        case_id: str | None,
        event_type: AuditEventType,
        agent_name: str,
        metadata: dict | None = None,
        error_message: str | None = None,
    ) -> AuditEventResponse:
        return self.create_event(
            AuditEventCreate(
                case_id=case_id,
                event_type=event_type,
                actor="system",
                actor_role=ReviewerRole.SYSTEM,
                action=self._default_action(event_type),
                description=f"Agent {agent_name} execution event.",
                agent_name=agent_name,
                error_message=error_message,
                metadata=metadata or {},
            )
        )

    def create_rag_retrieval_event(
        self,
        case_id: str | None,
        event_type: AuditEventType,
        rag_query: str,
        rag_sources: list[str] | None = None,
        metadata: dict | None = None,
        error_message: str | None = None,
    ) -> AuditEventResponse:
        return self.create_event(
            AuditEventCreate(
                case_id=case_id,
                event_type=event_type,
                actor="system",
                actor_role=ReviewerRole.SYSTEM,
                action=self._default_action(event_type),
                description="RAG retrieval event.",
                rag_query=rag_query,
                rag_sources=rag_sources or [],
                error_message=error_message,
                metadata=metadata or {},
            )
        )

    def create_human_decision_event(
        self,
        case_id: str,
        actor: str,
        actor_role: ReviewerRole,
        decision: str,
        reason_code: str,
        ai_recommendation: str | None,
        human_override: bool,
        comment: str | None = None,
        metadata: dict | None = None,
    ) -> AuditEventResponse:
        return self.record_event(
            case_id=case_id,
            event_type=AuditEventType.HUMAN_DECISION_SUBMITTED,
            actor=actor,
            actor_role=actor_role,
            decision=decision,
            reason_code=reason_code,
            comment=comment,
            ai_recommendation=ai_recommendation,
            human_decision=decision,
            human_override=human_override,
            metadata=metadata or {},
        )

    def create_human_override_event(
        self,
        case_id: str,
        actor: str,
        actor_role: ReviewerRole,
        ai_recommendation: str | None,
        human_decision: str,
        override_reason: str | None,
    ) -> AuditEventResponse:
        return self.create_event(
            AuditEventCreate(
                case_id=case_id,
                event_type=AuditEventType.HUMAN_OVERRIDE_DETECTED,
                actor=actor,
                actor_role=actor_role,
                action=self._default_action(AuditEventType.HUMAN_OVERRIDE_DETECTED),
                description=f"Human reviewer overrode AI recommendation from {ai_recommendation} to {human_decision}",
                ai_recommendation=ai_recommendation,
                human_decision=human_decision,
                human_override=True,
                override_reason=override_reason,
            )
        )

    def create_case_closed_event(self, case_id: str, actor: str, actor_role: ReviewerRole, comment: str | None = None) -> AuditEventResponse:
        return self.record_event(case_id, AuditEventType.CASE_CLOSED, actor, actor_role, comment=comment)

    def create_error_event(
        self,
        error_code: str,
        error_message: str,
        case_id: str | None = None,
        metadata: dict | None = None,
    ) -> AuditEventResponse:
        return self.create_event(
            AuditEventCreate(
                case_id=case_id,
                event_type=AuditEventType.API_ERROR,
                actor="system",
                actor_role=ReviewerRole.SYSTEM,
                action="API error",
                description=error_message,
                error_code=error_code,
                error_message=error_message,
                metadata=metadata or {},
            )
        )

    def get_case_audit_trail(self, case_id: str) -> AuditEventListResponse:
        events = [AuditEventResponse(**event) for event in self.repository.list_events_by_case_id(case_id)]
        return AuditEventListResponse(case_id=case_id, count=len(events), events=events)

    def search_audit_events(
        self,
        case_id: str | None = None,
        event_type: str | None = None,
        actor: str | None = None,
        actor_role: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> AuditEventListResponse:
        events = [
            AuditEventResponse(**event)
            for event in self.repository.search_events(case_id, event_type, actor, actor_role, start_date, end_date)
        ]
        return AuditEventListResponse(case_id=case_id, count=len(events), events=events)

    def get_entries(self, case_id: str) -> list[AuditEventResponse]:
        return self.get_case_audit_trail(case_id).events

    def clear_case(self, case_id: str) -> None:
        events = [event for event in self.repository.list_all_events() if event.get("case_id") != case_id]
        self.repository.replace_all(events)

    @staticmethod
    def _generate_audit_id(timestamp: datetime) -> str:
        return f"AUDIT-{timestamp.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"

    @staticmethod
    def _default_action(event_type: AuditEventType) -> str:
        return event_type.value.replace("_", " ").title()

    @staticmethod
    def _default_description(event_type: AuditEventType, previous_status: str | None, new_status: str | None, comment: str | None) -> str:
        if previous_status and new_status:
            return f"Status changed from {previous_status} to {new_status}."
        return comment or AuditService._default_action(event_type)


audit_service = AuditService()
