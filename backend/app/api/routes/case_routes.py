from fastapi import APIRouter

from app.repositories.case_repository import CaseRepository
from app.schemas.case_schema import CaseDetail, CaseSummary
from app.schemas.investigation_schema import InvestigationPackage
from app.services.audit_service import audit_service
from app.services.case_service import CaseService
from app.services.case_status_service import case_status_service
from app.services.investigation_service import InvestigationService

router = APIRouter(prefix="/cases", tags=["cases"])
case_repository = CaseRepository()
case_service = CaseService(case_repository, audit_service, case_status_service)
investigation_service = InvestigationService(case_repository, audit_service, case_status_service)


@router.get("", response_model=list[CaseSummary])
def list_cases() -> list[CaseSummary]:
    return case_service.list_cases()


@router.get("/{case_id}", response_model=CaseDetail)
def get_case(case_id: str) -> CaseDetail:
    return case_service.get_case_detail(case_id)


@router.post("/{case_id}/investigate", response_model=InvestigationPackage)
def investigate_case(case_id: str) -> InvestigationPackage:
    return investigation_service.investigate_case(case_id)
