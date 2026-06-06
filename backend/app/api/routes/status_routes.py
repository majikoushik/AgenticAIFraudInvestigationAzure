from fastapi import APIRouter

from app.repositories.case_repository import CaseRepository
from app.schemas.status_schema import CaseStatusResponse, CaseStatusUpdateRequest, CaseStatusUpdateResponse
from app.services.case_service import CaseService
from app.services.case_status_service import case_status_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/cases", tags=["case-status"])
case_repository = CaseRepository()
case_service = CaseService(case_repository, audit_service, case_status_service)


@router.get("/{case_id}/status", response_model=CaseStatusResponse)
def get_case_status(case_id: str) -> CaseStatusResponse:
    detail = case_service.get_case_detail(case_id)
    return CaseStatusResponse(
        case_id=case_id,
        status=detail.current_status,
        allowed_next_statuses=case_status_service.get_allowed_next_statuses(detail.current_status),
        status_updated_at=detail.status_updated_at,
        status_updated_by=detail.status_updated_by,
        status_comment=detail.status_comment,
    )


@router.patch("/{case_id}/status", response_model=CaseStatusUpdateResponse)
def update_case_status(case_id: str, request: CaseStatusUpdateRequest) -> CaseStatusUpdateResponse:
    result = case_status_service.transition_case_status(
        case_id=case_id,
        target_status=request.target_status,
        actor=request.actor,
        actor_role=request.actor_role,
        comment=request.comment,
    )
    return CaseStatusUpdateResponse(**result)
