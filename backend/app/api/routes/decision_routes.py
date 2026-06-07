from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission, validate_decision_permission
from app.core.constants import ReviewerRole
from app.repositories.case_repository import CaseRepository
from app.schemas.decision_schema import DecisionRequest, DecisionResponse
from app.services.audit_service import audit_service
from app.services.case_service import CaseService
from app.services.case_status_service import case_status_service

router = APIRouter(prefix="/cases", tags=["decisions"])
case_service = CaseService(CaseRepository(), audit_service, case_status_service)


@router.post("/{case_id}/decision", response_model=DecisionResponse)
def submit_decision(
    case_id: str,
    request: DecisionRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.SUBMIT_HUMAN_REVIEW)),
) -> DecisionResponse:
    validate_decision_permission(current_user, request.decision)
    request.reviewed_by = current_user.user_id
    return case_service.submit_decision(case_id, request, ReviewerRole(current_user.primary_role))
