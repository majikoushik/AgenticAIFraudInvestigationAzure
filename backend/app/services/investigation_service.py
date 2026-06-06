from pathlib import Path
import sys

from app.repositories.case_repository import CaseRepository
from app.schemas.investigation_schema import InvestigationPackage
from app.services.audit_service import AuditService
from app.services.case_service import CaseService


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
        orchestrator: FraudInvestigationOrchestrator | None = None,
    ) -> None:
        self.case_service = CaseService(repository, audit_service)
        self.orchestrator = orchestrator or FraudInvestigationOrchestrator()

    def investigate_case(self, case_id: str) -> InvestigationPackage:
        case_detail = self.case_service.get_case_detail(case_id)
        investigation = self.orchestrator.investigate(case_detail.model_dump())
        return InvestigationPackage(**investigation)
