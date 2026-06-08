from app.feedback.feedback_analytics_service import FeedbackAnalyticsService
from app.feedback.feedback_backlog_service import FeedbackBacklogService
from app.feedback.feedback_repository import FeedbackRepository


def test_analytics_summary_calculates_negative_rate(tmp_path) -> None:
    repo = FeedbackRepository(tmp_path / "feedback.json")
    backlog = FeedbackBacklogService(tmp_path / "backlog.json")
    repo.append_feedback({"feedback_id": "FB-1", "case_id": "case-001", "target_type": "AI_RECOMMENDATION", "rating": "POOR", "issue_types": ["INCORRECT_RECOMMENDATION"], "severity": "HIGH", "created_at": "2026-01-01T00:00:00Z"})
    analytics = FeedbackAnalyticsService(repo, backlog).get_all_metrics()
    assert analytics["summary"]["total_feedback"] == 1
    assert analytics["summary"]["negative_feedback_rate_percentage"] == 100.0
