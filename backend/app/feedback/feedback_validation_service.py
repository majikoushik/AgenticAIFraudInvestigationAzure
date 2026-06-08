from app.core.constants import FeedbackIssueType, FeedbackRating, FeedbackSeverity
from app.feedback.feedback_config import feedback_config
from app.schemas.feedback_schema import FeedbackCreateRequest, FeedbackDispositionUpdateRequest
from app.services.errors import ApiError


class FeedbackValidationService:
    def validate_feedback_create(self, request: FeedbackCreateRequest, case: dict | None = None) -> None:
        if not request.case_id.strip():
            raise ApiError(400, "feedback_case_required", "case_id is required.")
        if request.rating in {FeedbackRating.VERY_POOR, FeedbackRating.POOR} and feedback_config.require_comment_for_negative_rating:
            comment = (request.comment or "").strip()
            if not comment:
                raise ApiError(400, "feedback_comment_required", "Negative feedback requires a comment.")
            if len(comment) < feedback_config.min_comment_length:
                raise ApiError(400, "feedback_comment_too_short", f"Negative feedback comment must be at least {feedback_config.min_comment_length} characters.")
        issues = set(request.issue_types)
        policy_issues = {FeedbackIssueType.WRONG_POLICY_CITATION, FeedbackIssueType.MISSING_POLICY_CITATION}
        if issues.intersection(policy_issues) and not (request.policy_source_file or "policy" in (request.comment or "").lower()):
            raise ApiError(400, "feedback_policy_context_required", "Policy citation feedback requires policy source metadata or policy context in the comment.")
        safety_issues = {FeedbackIssueType.SAFETY_CONCERN, FeedbackIssueType.PII_CONCERN, FeedbackIssueType.PROMPT_INJECTION_CONCERN}
        if issues.intersection(safety_issues) and request.severity not in {FeedbackSeverity.HIGH, FeedbackSeverity.CRITICAL}:
            raise ApiError(400, "feedback_safety_severity_required", "Safety, PII, and prompt-injection concerns require HIGH or CRITICAL severity.")

    def validate_disposition_update(self, request: FeedbackDispositionUpdateRequest) -> None:
        if not request.disposition:
            raise ApiError(400, "feedback_disposition_required", "Disposition is required.")
