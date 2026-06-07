from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser, mask_email
from app.auth.permissions import Permission, require_permission
from app.core.constants import AuditEventType, ReviewerRole
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
def list_cases(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_CASES))) -> list[CaseSummary]:
    del current_user
    return case_service.list_cases()


@router.get("/{case_id}", response_model=CaseDetail)
def get_case(case_id: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_CASE_DETAILS))) -> CaseDetail:
    detail = case_service.get_case_detail(case_id)
    audit_service.record_event(
        case_id=case_id,
        event_type=AuditEventType.CASE_VIEWED,
        actor=current_user.user_id,
        actor_role=ReviewerRole(current_user.primary_role),
        metadata={"auth_mode": current_user.auth_mode, "email": mask_email(current_user.email)},
    )
    return detail


@router.post("/{case_id}/investigate", response_model=InvestigationPackage)
def investigate_case(case_id: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.RUN_AI_INVESTIGATION))) -> InvestigationPackage:
    del current_user
    return investigation_service.investigate_case(case_id)
