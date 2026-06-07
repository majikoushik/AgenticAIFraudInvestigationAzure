import json
import logging

from agents.agents.base_agent import BaseAgent
from agents.llm.llm_client_factory import LLMClientFactory
from agents.orchestration.state_manager import InvestigationState
from agents.safety.guardrail_engine import GuardrailEngine

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    name = "ReviewerAgent"

    def __init__(self) -> None:
        self.llm_client = LLMClientFactory.create()
        self.guardrails = GuardrailEngine()

    def run(self, state: InvestigationState) -> dict:
        logger.info("Agent started.", extra={"agent": self.name, "llm_provider": self.llm_client.get_provider_name()})
        summary = state.outputs["CaseSummaryAgent"]
        llm_response = self._generate_llm_validation(summary)
        validation = llm_response.get("json") or {}
        if llm_response.get("error") or "is_evidence_supported" not in validation:
            logger.info("Fallback mode used.", extra={"agent": self.name, "llm_provider": "local"})
            validation = self._generate_local_validation(summary)
            llm_response["fallback_used"] = self.llm_client.get_provider_name() != "local"

        guardrail_result = self.guardrails.validate_summary(summary)
        validation["safety_flags"] = sorted(set(validation.get("safety_flags", []) + guardrail_result["safety_flags"]))
        validation["citation_issues"] = guardrail_result.get("citation_issues", [])
        validation["policy_alignment"] = validation.get("policy_alignment", "ALIGNED" if not validation["citation_issues"] else "PARTIALLY_ALIGNED")
        validation["llm_provider"] = self.llm_client.get_provider_name()
        validation["llm_response_metadata"] = CaseSummaryResponseMetadata.from_response(llm_response)
        validation["review_notes"] = [
            validation.get("reviewer_notes", ""),
            "Recommendation is framed as investigator assistance, not an autonomous fraud accusation.",
            "High-impact actions require human review before execution.",
        ]
        validation["human_review_required"] = True
        logger.info("Agent completed.", extra={"agent": self.name, "llm_provider": self.llm_client.get_provider_name()})
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
        response = self.llm_client.generate_json(prompt, system_prompt=system_prompt, metadata={"agent": self.name})
        local = self._generate_local_validation(summary)
        generated = response.get("json") or {}
        response["json"] = {**local, **{key: value for key, value in generated.items() if key in local}}
        return response

    def _generate_local_validation(self, summary: dict) -> dict:
        unsupported_claims = []

        if summary["recommended_action"] in {"hold", "escalate", "reject"} and not summary["key_risk_indicators"]:
            unsupported_claims.append("Recommended action requires at least one risk indicator.")

        if summary["recommended_action"] == "reject":
            unsupported_claims.append("Reject is high-impact and should not be recommended by the MVP agents.")

        grounding = summary.get("grounding", {})
        if summary["recommended_action"] in {"hold", "escalate"} and grounding.get("policy_citation_count", 0) == 0:
            unsupported_claims.append("Hold or escalate recommendation requires at least one policy citation.")

        return {
            "is_evidence_supported": len(unsupported_claims) == 0,
            "unsupported_claims": unsupported_claims,
            "human_review_required": True,
            "reviewer_notes": "Recommendation is evidence-supported when risk indicators and policy references are present.",
            "safety_flags": [],
        }


class CaseSummaryResponseMetadata:
    @staticmethod
    def from_response(response: dict) -> dict:
        return {
            "provider": response.get("provider", "local"),
            "model": response.get("model", ""),
            "usage": response.get("usage", {}),
            "latency_ms": response.get("latency_ms", 0),
            "finish_reason": response.get("finish_reason", "unknown"),
            "error": response.get("error"),
            "fallback_used": response.get("fallback_used", False),
        }
