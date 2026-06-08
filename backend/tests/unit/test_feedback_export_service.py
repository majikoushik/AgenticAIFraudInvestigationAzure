from app.feedback.feedback_export_service import FeedbackExportService
from app.feedback.feedback_repository import FeedbackRepository


def test_export_sanitizes_eval_dataset(tmp_path) -> None:
    repo = FeedbackRepository(tmp_path / "feedback.json")
    repo.append_feedback({"feedback_id": "FB-1", "case_id": "case-001", "target_type": "AI_RECOMMENDATION", "rating": "POOR", "issue_types": ["INCORRECT_RECOMMENDATION"], "severity": "HIGH", "disposition": "ACCEPTED_FOR_IMPROVEMENT", "comment": "Expected escalation.", "raw_prompt": "do not export", "created_at": "2026-01-01T00:00:00Z"})
    result = FeedbackExportService(repo).export_feedback_to_eval_dataset(target_path=str(tmp_path / "eval.json"))
    assert result["exported_count"] == 1
    assert "raw_prompt" not in str(result["eval_cases"])
