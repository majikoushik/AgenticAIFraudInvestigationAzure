import json
import logging

from agents.agents.base_agent import BaseAgent
from agents.llm.llm_client_factory import LLMClientFactory
from agents.orchestration.guardrail_engine import GuardrailEngine
from agents.orchestration.state_manager import InvestigationState

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    name = "ReviewerAgent"

    def __init__(self) -> None:
        self.llm_client = LLMClientFactory.create()
        self.guardrails = GuardrailEngine()

    def run(self, state: InvestigationState) -> dict:
        logger.info("Agent started.", extra={"agent": self.name, "llm_provider": self.llm_client.provider_name})
        summary = state.outputs["CaseSummaryAgent"]
        if self.llm_client.provider_name != "local" and self.llm_client.is_available():
            validation = self._generate_llm_validation(summary)
        else:
            logger.info("Fallback mode used.", extra={"agent": self.name, "llm_provider": "local"})
            validation = self._generate_local_validation(summary)

        guardrail_result = self.guardrails.validate_summary(summary)
        validation["safety_flags"] = sorted(set(validation.get("safety_flags", []) + guardrail_result["safety_flags"]))
        validation["llm_provider"] = self.llm_client.provider_name
        validation["review_notes"] = [
            validation.get("reviewer_notes", ""),
            "Recommendation is framed as investigator assistance, not an autonomous fraud accusation.",
            "High-impact actions require human review before execution.",
        ]
        logger.info("Agent completed.", extra={"agent": self.name, "llm_provider": self.llm_client.provider_name})
        return validation

    def _generate_llm_validation(self, summary: dict) -> dict:
        prompt = json.dumps(
            {
                "investigation_summary": summary,
                "required_schema": {
                    "is_evidence_supported": True,
                    "unsupported_claims": [],
                    "human_review_required": True,
                    "reviewer_notes": "string",
                    "safety_flags": [],
                },
            },
            default=str,
        )
        system_prompt = (
            "You are a reviewer agent. Return valid JSON only. Check evidence support, "
            "policy citation, unsupported claims, and human review guardrails."
        )
        generated = self.llm_client.generate_json(prompt, system_prompt=system_prompt)
        local = self._generate_local_validation(summary)
        return {**local, **{key: value for key, value in generated.items() if key in local}}

    def _generate_local_validation(self, summary: dict) -> dict:
        unsupported_claims = []

        if summary["recommended_action"] in {"hold", "escalate", "reject"} and not summary["key_risk_indicators"]:
            unsupported_claims.append("Recommended action requires at least one risk indicator.")

        if summary["recommended_action"] == "reject":
            unsupported_claims.append("Reject is high-impact and should not be recommended by the MVP agents.")

        return {
            "is_evidence_supported": len(unsupported_claims) == 0,
            "unsupported_claims": unsupported_claims,
            "human_review_required": True,
            "reviewer_notes": "Recommendation is evidence-supported when risk indicators and policy references are present.",
            "safety_flags": [],
        }
