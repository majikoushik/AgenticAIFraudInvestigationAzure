from app.auth.current_user import AuthenticatedUser
from app.feedback.feedback_backlog_service import FeedbackBacklogService
from app.feedback.feedback_repository import FeedbackRepository
from app.feedback.feedback_service import FeedbackService
from app.repositories.case_repository import CaseRepository
from app.schemas.feedback_schema import FeedbackCreateRequest


class FakeCaseRepository(CaseRepository):
    def get_case_by_id(self, case_id: str) -> dict | None:
        return {"case_id": case_id, "status": "PENDING_HUMAN_REVIEW", "severity": "high", "ai_recommendation": "HOLD", "risk_indicators": [{"code": "NEW_DEVICE"}]}


def test_submit_feedback_and_critical_backlog(tmp_path) -> None:
    service = FeedbackService(
        repository=FeedbackRepository(tmp_path / "feedback.json"),
        backlog_service=FeedbackBacklogService(tmp_path / "backlog.json"),
        case_repository=FakeCaseRepository(),
    )
    user = AuthenticatedUser(user_id="fraud_analyst_01", email="demo@example.com", roles=["FRAUD_ANALYST"], primary_role="FRAUD_ANALYST", auth_mode="local")
    request = FeedbackCreateRequest(case_id="case-001", target_type="AI_RECOMMENDATION", rating="POOR", issue_types=["HALLUCINATION_SUSPECTED"], severity="CRITICAL", comment="This recommendation contains unsupported details.", expected_recommendation="ESCALATE")

    feedback = service.submit_feedback(request, user)

    assert feedback["feedback_id"].startswith("FB-")
    assert service.backlog_service.list_backlog_items()[0]["backlog_type"] == "SAFETY_REVIEW"
