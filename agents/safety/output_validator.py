import os
from typing import Any

from agents.observability.llm_telemetry import track_llm_event

try:
    from app.observability import telemetry_events
except Exception:  # pragma: no cover
    telemetry_events = None


class OutputValidator:
    allowed_actions = {"APPROVE", "HOLD", "ESCALATE", "REJECT", "approve", "hold", "escalate", "reject"}
    allowed_confidence = {"LOW", "MEDIUM", "HIGH", "low", "medium", "high"}
    accusation_terms = ["customer committed fraud", "customer is fraudulent", "criminal", "fraudster"]
    autonomous_action_terms = ["freeze account immediately without review", "permanently block customer"]

    def validate_summary(self, summary: dict[str, Any]) -> dict[str, Any]:
        errors = []
        flags = []
        action = summary.get("recommended_action")
        confidence = summary.get("confidence_level")
        text = str(summary).lower()

        if action not in self.allowed_actions:
            errors.append("INVALID_RECOMMENDED_ACTION")
        if confidence not in self.allowed_confidence:
            errors.append("INVALID_CONFIDENCE_LEVEL")
        if summary.get("human_review_required") is not True and not summary.get("human_review_requirement"):
            errors.append("HUMAN_REVIEW_REQUIRED")
        if os.getenv("AI_SAFETY_REQUIRE_CITATIONS", "true").lower() == "true" and action in {"HOLD", "ESCALATE", "REJECT", "hold", "escalate", "reject"}:
            if not summary.get("policy_references"):
                errors.append("POLICY_CITATION_MISSING")
        if any(term in text for term in self.accusation_terms):
            flags.append("DIRECT_ACCUSATION_NOT_ALLOWED")
        if any(term in text for term in self.autonomous_action_terms):
            flags.append("AUTONOMOUS_FINAL_ACTION_NOT_ALLOWED")
        if "missing_evidence" not in summary:
            errors.append("MISSING_EVIDENCE_NOT_MARKED")

        passed = not errors and not flags
        if not passed and telemetry_events:
            track_llm_event(telemetry_events.LLM_OUTPUT_VALIDATION_FAILED, {"validation_errors": errors, "safety_flag_count": len(flags)})
        return {"passed": passed, "validation_errors": errors, "safety_flags": flags}
