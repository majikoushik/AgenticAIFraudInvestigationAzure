from app.auth.current_user import AuthenticatedUser
from app.feedback.feedback_service import feedback_service


def capture_override_feedback(case_id: str, review_result: dict, current_user: AuthenticatedUser) -> dict | None:
    return feedback_service.create_feedback_from_human_review(case_id, review_result, current_user)
