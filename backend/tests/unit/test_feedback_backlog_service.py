from app.feedback.feedback_backlog_service import FeedbackBacklogService


def test_backlog_mapping_and_creation(tmp_path) -> None:
    service = FeedbackBacklogService(tmp_path / "backlog.json")
    feedback = {"feedback_id": "FB-1", "case_id": "case-001", "target_type": "AI_RECOMMENDATION", "issue_types": ["INCORRECT_RECOMMENDATION"], "severity": "HIGH", "comment": "Recommendation should escalate."}
    item = service.create_backlog_item_from_feedback(feedback)
    assert item["backlog_type"] == "PROMPT_IMPROVEMENT"
    assert service.list_backlog_items()[0]["backlog_id"] == item["backlog_id"]
