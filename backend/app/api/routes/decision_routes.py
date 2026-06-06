from fastapi import APIRouter

from app.repositories.case_repository import CaseRepository
from app.schemas.decision_schema import DecisionRequest, DecisionResponse
from app.services.audit_service import audit_service
from app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["decisions"])
case_service = CaseService(CaseRepository(), audit_service)


@router.post("/{case_id}/decision", response_model=DecisionResponse)
def submit_decision(case_id: str, request: DecisionRequest) -> DecisionResponse:
    return case_service.submit_decision(case_id, request)
