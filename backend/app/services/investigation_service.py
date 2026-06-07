from pathlib import Path
import sys

from app.core.constants import AuditEventType, CaseStatus, ReviewerRole
from app.repositories.case_repository import CaseRepository
from app.schemas.investigation_schema import InvestigationPackage
from app.services.audit_service import AuditService
from app.services.case_service import CaseService
from app.services.case_status_service import CaseStatusService, case_status_service
from app.cost.token_usage_service import TokenUsageService


def _ensure_project_root_on_path() -> None:
    project_root = Path(__file__).resolve().parents[3]
    project_root_text = str(project_root)
    if project_root_text not in sys.path:
        sys.path.append(project_root_text)


_ensure_project_root_on_path()

from agents.orchestration.orchestrator import FraudInvestigationOrchestrator  # noqa: E402


class InvestigationService:
    def __init__(
        self,
        repository: CaseRepository,
        audit_service: AuditService,
        status_service: CaseStatusService = case_status_service,
        orchestrator: FraudInvestigationOrchestrator | None = None,
        token_usage_service: TokenUsageService | None = None,
    ) -> None:
        self.case_service = CaseService(repository, audit_service, status_service)
        self.audit_service = audit_service
        self.status_service = status_service
        self.orchestrator = orchestrator or FraudInvestigationOrchestrator()
        self.token_usage_service = token_usage_service or TokenUsageService()

    def investigate_case(self, case_id: str) -> InvestigationPackage:
        current_status = self.case_service.get_status(case_id)
        if current_status != CaseStatus.NEW:
            from app.services.errors import ApiError

            raise ApiError(400, "invalid_status_transition", "AI investigation can only be started from NEW.")

        self.status_service.transition_case_status(
            case_id,
            CaseStatus.AI_INVESTIGATION_IN_PROGRESS.value,
            actor="system",
            actor_role="SYSTEM",
            comment="AI investigation started",
        )
        case_detail = self.case_service.get_case_detail(case_id)
        try:
            investigation = self.orchestrator.investigate(case_detail.model_dump())
        except Exception:
            self.audit_service.record_event(
                case_id=case_id,
                event_type=AuditEventType.AI_INVESTIGATION_FAILED,
                actor="system",
                actor_role=ReviewerRole.SYSTEM,
                previous_status=CaseStatus.AI_INVESTIGATION_IN_PROGRESS.value,
                new_status=CaseStatus.AI_INVESTIGATION_IN_PROGRESS.value,
                comment="AI investigation failed; manual review required",
            )
            raise

        self.case_service.set_investigation_result(case_id, investigation)
        self._record_token_usage(case_id, investigation)
        self.status_service.transition_case_status(
            case_id,
            CaseStatus.AI_INVESTIGATION_COMPLETED.value,
            actor="system",
            actor_role="SYSTEM",
            comment="AI investigation completed",
        )
        self.status_service.transition_case_status(
            case_id,
            CaseStatus.PENDING_HUMAN_REVIEW.value,
            actor="system",
            actor_role="SYSTEM",
            comment="Case is ready for human review",
        )
        investigation["final_case_status"] = CaseStatus.PENDING_HUMAN_REVIEW.value
        return InvestigationPackage(**investigation)

    def _record_token_usage(self, case_id: str, investigation: dict) -> None:
        for record in investigation.get("token_usage_records", []):
            self.token_usage_service.record_token_usage(
                case_id=case_id,
                agent_name=record.get("agent_name", "UNKNOWN"),
                operation_name=record.get("operation_name", "agent_llm_call"),
                ai_provider=record.get("ai_provider", investigation.get("ai_provider", "local")),
                model_or_deployment=record.get("model_or_deployment", ""),
                prompt_tokens=record.get("prompt_tokens", 0),
                completion_tokens=record.get("completion_tokens", 0),
                metadata={
                    "latency_ms": record.get("latency_ms", 0),
                    "fallback_used": record.get("fallback_used", False),
                    "retry_count": record.get("retry_count", 0),
                },
                success=record.get("success", True),
                error_type=record.get("error_type"),
            )
