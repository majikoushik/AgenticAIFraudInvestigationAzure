import json
import re
from typing import Any

from agents.observability.llm_telemetry import track_llm_event

try:
    from app.observability import telemetry_events
except Exception:  # pragma: no cover
    telemetry_events = None


class LLMResponseParser:
    required_summary_fields = {
        "case_overview",
        "key_risk_indicators",
        "evidence_supporting_suspicion",
        "evidence_reducing_suspicion",
        "policy_references",
        "similar_cases",
        "recommended_action",
        "confidence_level",
        "missing_evidence",
        "human_review_required",
    }

    def parse_json(self, content: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(content, dict):
            return {"parsed": content, "errors": []}

        try:
            parsed = json.loads(content)
            return {"parsed": parsed, "errors": []}
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, flags=re.DOTALL)
            if not match:
                if telemetry_events:
                    track_llm_event(telemetry_events.LLM_JSON_PARSE_FAILED, {"reason": "invalid_json"})
                return {"parsed": {}, "errors": ["invalid_json"]}
            try:
                return {"parsed": json.loads(match.group(0)), "errors": ["json_extracted_from_text"]}
            except json.JSONDecodeError:
                if telemetry_events:
                    track_llm_event(telemetry_events.LLM_JSON_PARSE_FAILED, {"reason": "repair_failed"})
                return {"parsed": {}, "errors": ["invalid_json"]}

    def normalize_summary(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(payload)
        if "recommended_action" in normalized:
            normalized["recommended_action"] = str(normalized["recommended_action"]).upper()
        if "confidence_level" in normalized:
            normalized["confidence_level"] = str(normalized["confidence_level"]).upper()
        normalized["human_review_required"] = True
        return normalized

    def validate_required_fields(self, payload: dict[str, Any], required_fields: set[str] | None = None) -> list[str]:
        required = required_fields or self.required_summary_fields
        return sorted(field for field in required if field not in payload)
