import logging

logger = logging.getLogger(__name__)


class GuardrailEngine:
    direct_accusation_terms = ["customer committed fraud", "customer is a fraudster", "fraudster"]
    permanent_freeze_terms = ["permanent account freeze", "freeze permanently", "permanently freeze"]

    def validate_summary(self, summary: dict) -> dict:
        safety_flags: list[str] = []
        text = str(summary).lower()

        if any(term in text for term in self.direct_accusation_terms):
            safety_flags.append("DIRECT_ACCUSATION_NOT_ALLOWED")

        if any(term in text for term in self.permanent_freeze_terms):
            safety_flags.append("PERMANENT_FREEZE_REQUIRES_HUMAN_REVIEW")

        if summary.get("recommended_action") in {"hold", "escalate", "reject"} and not summary.get("key_risk_indicators"):
            safety_flags.append("DECISION_WITHOUT_EVIDENCE")

        if "missing_evidence" not in summary:
            safety_flags.append("MISSING_EVIDENCE_NOT_MARKED")

        if summary.get("recommended_action") in {"hold", "escalate", "reject"} and not summary.get("policy_references"):
            safety_flags.append("POLICY_CITATION_MISSING")

        high_value = any(
            indicator.get("code") in {"HIGH_AMOUNT", "HIGH_VALUE_TRANSFER"}
            for indicator in summary.get("key_risk_indicators", [])
        )
        if high_value and not summary.get("human_review_requirement"):
            safety_flags.append("HIGH_VALUE_REQUIRES_HUMAN_REVIEW")

        for flag in safety_flags:
            logger.warning("Guardrail violation detected.", extra={"guardrail_flag": flag})

        return {
            "passed": len(safety_flags) == 0,
            "safety_flags": safety_flags,
        }
