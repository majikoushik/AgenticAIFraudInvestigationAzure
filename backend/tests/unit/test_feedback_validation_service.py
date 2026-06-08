import pytest

from app.core.constants import FeedbackIssueType, FeedbackRating, FeedbackSeverity, FeedbackTargetType
from app.feedback.feedback_validation_service import FeedbackValidationService
from app.schemas.feedback_schema import FeedbackCreateRequest
from app.services.errors import ApiError


def test_negative_rating_requires_comment() -> None:
    request = FeedbackCreateRequest(case_id="case-001", target_type=FeedbackTargetType.AI_RECOMMENDATION, rating=FeedbackRating.POOR, severity=FeedbackSeverity.HIGH)
    with pytest.raises(ApiError):
        FeedbackValidationService().validate_feedback_create(request)


def test_wrong_policy_citation_accepts_policy_metadata() -> None:
    request = FeedbackCreateRequest(case_id="case-001", target_type=FeedbackTargetType.POLICY_CITATION, rating=FeedbackRating.POOR, severity=FeedbackSeverity.HIGH, issue_types=[FeedbackIssueType.WRONG_POLICY_CITATION], comment="Wrong policy citation was selected.", policy_source_file="policy.md")
    FeedbackValidationService().validate_feedback_create(request)
