from app.feedback.feedback_repository import FeedbackRepository


def test_feedback_repository_creates_store_and_filters(tmp_path) -> None:
    repo = FeedbackRepository(tmp_path / "ai_feedback.json")
    assert repo.list_feedback() == []
    repo.append_feedback({"feedback_id": "FB-1", "case_id": "case-001", "target_type": "AI_RECOMMENDATION", "rating": "GOOD", "issue_types": [], "severity": "LOW", "created_at": "2026-01-01T00:00:00Z"})
    assert repo.get_feedback_by_id("FB-1") is not None
    assert len(repo.search_feedback(case_id="case-001")) == 1
