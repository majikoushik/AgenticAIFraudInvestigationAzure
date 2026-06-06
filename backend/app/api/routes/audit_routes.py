from fastapi import APIRouter

from app.repositories.case_repository import CaseRepository
from app.schemas.audit_schema import AuditTrailResponse
from app.services.audit_service import audit_service
from app.services.case_service import CaseService
from app.services.case_status_service import case_status_service

router = APIRouter(prefix="/cases", tags=["audit"])
case_service = CaseService(CaseRepository(), audit_service, case_status_service)


@router.get("/{case_id}/audit", response_model=AuditTrailResponse)
def get_case_audit(case_id: str) -> AuditTrailResponse:
    case_service.ensure_case_exists(case_id)
    return AuditTrailResponse(case_id=case_id, events=audit_service.get_entries(case_id))
