from pathlib import Path
import sys

from app.core.constants import AuditEventType, CaseStatus, ReviewerRole
from app.repositories.case_repository import CaseRepository
from app.schemas.investigation_schema import InvestigationPackage
from app.services.audit_service import AuditService
from app.services.case_service import CaseService
from app.services.case_status_service import CaseStatusService, case_status_service


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
    ) -> None:
        self.case_service = CaseService(repository, audit_service, status_service)
        self.audit_service = audit_service
        self.status_service = status_service
        self.orchestrator = orchestrator or FraudInvestigationOrchestrator()

    def investigate_case(self, case_id: str) -> InvestigationPackage:
        current_status = self.case_service.get_status(case_id)
        previous_status, new_status = self.status_service.transition(
            case_id,
            current_status,
            CaseStatus.AI_INVESTIGATION_IN_PROGRESS,
        )
        self.audit_service.record_event(
            case_id=case_id,
            event_type=AuditEventType.AI_INVESTIGATION_STARTED,
            actor="system",
            actor_role=ReviewerRole.SYSTEM,
            previous_status=previous_status.value,
            new_status=new_status.value,
        )
        case_detail = self.case_service.get_case_detail(case_id)
        investigation = self.orchestrator.investigate(case_detail.model_dump())
        self.case_service.set_investigation_result(case_id, investigation)

        previous_status, new_status = self.status_service.transition(
            case_id,
            CaseStatus.AI_INVESTIGATION_IN_PROGRESS,
            CaseStatus.AI_INVESTIGATION_COMPLETED,
        )
        self.audit_service.record_event(
            case_id=case_id,
            event_type=AuditEventType.AI_INVESTIGATION_COMPLETED,
            actor="system",
            actor_role=ReviewerRole.SYSTEM,
            previous_status=previous_status.value,
            new_status=new_status.value,
            ai_recommendation=self.case_service.get_ai_recommendation(case_id),
        )
        previous_status, new_status = self.status_service.transition(
            case_id,
            CaseStatus.AI_INVESTIGATION_COMPLETED,
            CaseStatus.PENDING_HUMAN_REVIEW,
        )
        self.audit_service.record_event(
            case_id=case_id,
            event_type=AuditEventType.CASE_STATUS_CHANGED,
            actor="system",
            actor_role=ReviewerRole.SYSTEM,
            previous_status=previous_status.value,
            new_status=new_status.value,
            ai_recommendation=self.case_service.get_ai_recommendation(case_id),
        )
        return InvestigationPackage(**investigation)
