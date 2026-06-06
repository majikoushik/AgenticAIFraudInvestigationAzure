from fastapi import APIRouter, Query

from app.core.constants import ReviewerRole
from app.repositories.case_repository import CaseRepository
from app.schemas.review_schema import (
    CloseCaseRequest,
    CloseCaseResponse,
    HumanReviewRequest,
    HumanReviewResponse,
    OverrideSummaryResponse,
    ReviewOptionsResponse,
)
from app.services.audit_service import audit_service
from app.services.case_status_service import case_status_service
from app.services.human_review_service import HumanReviewService

router = APIRouter(prefix="/cases", tags=["human-review"])
review_service = HumanReviewService(CaseRepository(), audit_service, case_status_service)


@router.post("/{case_id}/review", response_model=HumanReviewResponse)
def submit_review(case_id: str, request: HumanReviewRequest) -> HumanReviewResponse:
    return review_service.submit_review(case_id, request)


@router.get("/{case_id}/override-summary", response_model=OverrideSummaryResponse)
def get_override_summary(case_id: str) -> OverrideSummaryResponse:
    return OverrideSummaryResponse(**review_service.get_override_summary(case_id))


@router.post("/{case_id}/close", response_model=CloseCaseResponse)
def close_case(case_id: str, request: CloseCaseRequest) -> CloseCaseResponse:
    return review_service.close_case(case_id, request)


@router.get("/{case_id}/review-options", response_model=ReviewOptionsResponse)
def get_review_options(
    case_id: str,
    reviewer_role: ReviewerRole = Query(...),
) -> ReviewOptionsResponse:
    del case_id
    return review_service.get_review_options(reviewer_role)
