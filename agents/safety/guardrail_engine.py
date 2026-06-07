from typing import Any

from agents.safety.citation_validator import CitationValidator
from agents.safety.output_validator import OutputValidator
from agents.safety.pii_redactor import PiiRedactor
from agents.safety.prompt_injection_detector import detect_prompt_injection
from agents.safety.recommendation_policy import enforce_human_review
from agents.observability.llm_telemetry import track_llm_event

try:
    from app.observability import telemetry_events
except Exception:  # pragma: no cover
    telemetry_events = None


class GuardrailEngine:
    def __init__(self) -> None:
        self.redactor = PiiRedactor()
        self.output_validator = OutputValidator()
        self.citation_validator = CitationValidator()

    def sanitize_input(self, data: dict[str, Any]) -> dict[str, Any]:
        return self.redactor.redact_dict(data)

    def validate_summary(self, summary: dict[str, Any], retrieved_references: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        summary = enforce_human_review(summary)
        output_result = self.output_validator.validate_summary(summary)
        citation_result = self.citation_validator.validate(summary.get("policy_references", []), retrieved_references or summary.get("policy_references", []))
        flags = sorted(set(output_result["safety_flags"] + [issue["issue"].upper() for issue in citation_result["citation_issues"]]))
        passed = output_result["passed"] and citation_result["passed"]
        if not passed and telemetry_events:
            track_llm_event(telemetry_events.GUARDRAIL_VIOLATION_DETECTED, {"safety_flag_count": len(flags), "validation_errors": output_result["validation_errors"]})
        return {
            "passed": passed,
            "flags": flags,
            "safety_flags": flags,
            "sanitized_input": {},
            "validation_errors": output_result["validation_errors"],
            "citation_issues": citation_result["citation_issues"],
            "requires_human_review": True,
        }

    def inspect_text(self, text: str) -> dict[str, Any]:
        return detect_prompt_injection(text)
