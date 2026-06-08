from fastapi import APIRouter, Depends, Query

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission, validate_decision_permission
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
from app.admin.feature_flag_service import FeatureFlagService
from app.services.errors import ApiError

router = APIRouter(prefix="/cases", tags=["human-review"])
review_service = HumanReviewService(CaseRepository(), audit_service, case_status_service)
feature_flags = FeatureFlagService()


@router.post("/{case_id}/review", response_model=HumanReviewResponse)
def submit_review(
    case_id: str,
    request: HumanReviewRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.SUBMIT_HUMAN_REVIEW)),
) -> HumanReviewResponse:
    if not feature_flags.is_enabled("FEATURE_ENABLE_HUMAN_REVIEW"):
        raise ApiError(403, "feature_disabled", "Human review feature is disabled by admin configuration.")
    validate_decision_permission(current_user, request.decision.value)
    request.reviewed_by = current_user.user_id
    request.reviewer_role = ReviewerRole(current_user.primary_role)
    return review_service.submit_review(case_id, request)


@router.get("/{case_id}/override-summary", response_model=OverrideSummaryResponse)
def get_override_summary(
    case_id: str,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_CASE_DETAILS)),
) -> OverrideSummaryResponse:
    del current_user
    return OverrideSummaryResponse(**review_service.get_override_summary(case_id))


@router.post("/{case_id}/close", response_model=CloseCaseResponse)
def close_case(
    case_id: str,
    request: CloseCaseRequest,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.CLOSE_CASE)),
) -> CloseCaseResponse:
    request.closed_by = current_user.user_id
    request.closer_role = ReviewerRole(current_user.primary_role)
    return review_service.close_case(case_id, request)


@router.get("/{case_id}/review-options", response_model=ReviewOptionsResponse)
def get_review_options(
    case_id: str,
    reviewer_role: ReviewerRole = Query(...),
) -> ReviewOptionsResponse:
    del case_id
    return review_service.get_review_options(reviewer_role)
