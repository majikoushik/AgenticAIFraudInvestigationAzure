import json
from pathlib import Path

from app.config import settings
from app.core.constants import FeedbackDisposition
from app.feedback.feedback_repository import FeedbackRepository
from app.feedback.feedback_sanitizer import sanitize_feedback_payload
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client


class FeedbackExportService:
    def __init__(self, repository: FeedbackRepository | None = None) -> None:
        self.repository = repository or FeedbackRepository()

    def export_feedback_to_eval_dataset(self, disposition_filter: str = FeedbackDisposition.ACCEPTED_FOR_IMPROVEMENT.value, target_path: str | None = None) -> dict:
        path = self._resolve(target_path or settings.feedback_export_path)
        records = self.repository.search_feedback(disposition=disposition_filter, limit=10000)
        eval_cases = [self._to_eval_case(record) for record in records]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(eval_cases, indent=2), encoding="utf-8")
        get_telemetry_client().track_event(telemetry_events.AI_FEEDBACK_EXPORTED_TO_EVAL, {"disposition_filter": disposition_filter}, {"feedback_count": len(eval_cases)})
        return {"exported_count": len(eval_cases), "target_path": str(path), "eval_cases": eval_cases}

    @staticmethod
    def _to_eval_case(feedback: dict) -> dict:
        clean = sanitize_feedback_payload(feedback)
        return {
            "eval_case_id": f"EVAL-{clean.get('feedback_id')}",
            "source_feedback_id": clean.get("feedback_id"),
            "case_id": clean.get("case_id"),
            "target_type": clean.get("target_type"),
            "issue_types": clean.get("issue_types", []),
            "input_context_summary": {
                "risk_indicators": clean.get("sanitized_ai_output_snapshot", {}).get("risk_indicators", []),
                "policy_references": clean.get("sanitized_ai_output_snapshot", {}).get("policy_references", []),
                "human_decision": clean.get("human_decision"),
                "ai_recommendation": clean.get("actual_ai_recommendation"),
            },
            "expected_behavior": {
                "expected_recommendation": clean.get("expected_recommendation"),
                "expected_citation_behavior": "Use retrieved policy citations only.",
                "expected_explanation": clean.get("suggested_correction") or clean.get("comment"),
            },
            "safety_expectations": {
                "human_review_required": True,
                "no_direct_fraud_accusation": True,
                "no_unsupported_claims": True,
            },
        }

    @staticmethod
    def _resolve(path_value: str) -> Path:
        path = Path(path_value)
        return path if path.is_absolute() else Path(__file__).resolve().parents[3] / path
