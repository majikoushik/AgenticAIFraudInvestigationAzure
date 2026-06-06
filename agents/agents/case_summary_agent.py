import json
import logging

from agents.agents.base_agent import BaseAgent
from agents.llm.llm_client_factory import LLMClientFactory
from agents.orchestration.guardrail_engine import GuardrailEngine
from agents.orchestration.state_manager import InvestigationState

logger = logging.getLogger(__name__)


class CaseSummaryAgent(BaseAgent):
    name = "CaseSummaryAgent"

    def __init__(self) -> None:
        self.llm_client = LLMClientFactory.create()
        self.guardrails = GuardrailEngine()

    def run(self, state: InvestigationState) -> dict:
        logger.info("Agent started.", extra={"agent": self.name, "llm_provider": self.llm_client.provider_name})
        if self.llm_client.provider_name != "local" and self.llm_client.is_available():
            summary = self._generate_llm_summary(state)
        else:
            logger.info("Fallback mode used.", extra={"agent": self.name, "llm_provider": "local"})
            summary = self._generate_local_summary(state)

        guardrail_result = self.guardrails.validate_summary(summary)
        summary["safety_flags"] = guardrail_result["safety_flags"]
        summary["llm_provider"] = self.llm_client.provider_name
        logger.info("Agent completed.", extra={"agent": self.name, "llm_provider": self.llm_client.provider_name})
        return summary

    def _generate_llm_summary(self, state: InvestigationState) -> dict:
        prompt = json.dumps(
            {
                "case": state.case,
                "agent_outputs": state.outputs,
                "required_schema": {
                    "case_overview": "string",
                    "key_risk_indicators": [],
                    "evidence_supporting_suspicion": [],
                    "evidence_reducing_suspicion": [],
                    "policy_references": [],
                    "similar_cases": [],
                    "recommended_action": "approve | hold | escalate | reject",
                    "confidence_level": "low | medium | high",
                    "missing_evidence": [],
                    "human_review_requirement": "string",
                },
            },
            default=str,
        )
        system_prompt = (
            "You are a fraud investigation assistant. Return valid JSON only. "
            "Do not accuse customers. Require human review for high-impact actions."
        )
        generated = self.llm_client.generate_json(prompt, system_prompt=system_prompt)
        local = self._generate_local_summary(state)
        return {**local, **{key: value for key, value in generated.items() if key in local}}

    def _generate_local_summary(self, state: InvestigationState) -> dict:
        risk_indicators = self._collect_risk_indicators(state)
        high_count = sum(1 for indicator in risk_indicators if indicator["severity"] == "high")
        medium_count = sum(1 for indicator in risk_indicators if indicator["severity"] == "medium")

        recommended_action = "escalate" if high_count >= 2 else "hold" if risk_indicators else "approve"
        confidence_level = "high" if high_count >= 2 else "medium" if medium_count >= 2 else "low"

        return {
            "case_overview": self._case_overview(state),
            "key_risk_indicators": risk_indicators,
            "evidence_supporting_suspicion": self._supporting_evidence(state, risk_indicators),
            "evidence_reducing_suspicion": self._reducing_evidence(state),
            "policy_references": state.outputs.get("PolicyRagAgent", {}).get("policy_references", []),
            "similar_cases": state.outputs.get("HistoricalCaseAgent", {}).get("similar_cases", []),
            "recommended_action": recommended_action,
            "confidence_level": confidence_level,
            "missing_evidence": self._missing_evidence(state),
            "human_review_requirement": "Human investigator review is required before any high-impact action.",
        }

    @staticmethod
    def _collect_risk_indicators(state: InvestigationState) -> list[dict]:
        indicators: list[dict] = []
        seen_codes: set[str] = set()

        for output in state.outputs.values():
            for indicator in output.get("risk_indicators", []):
                if indicator["code"] not in seen_codes:
                    indicators.append(indicator)
                    seen_codes.add(indicator["code"])

        for indicator in state.case.get("initial_risk_indicators", []):
            if indicator["code"] not in seen_codes:
                indicators.append(indicator)
                seen_codes.add(indicator["code"])

        return indicators

    @staticmethod
    def _case_overview(state: InvestigationState) -> str:
        case_id = state.case["metadata"]["case_id"]
        customer_id = state.case["customer"]["customer_id"]
        amount = state.case["suspicious_transaction"]["amount"]
        currency = state.case["suspicious_transaction"]["currency"]
        return f"{case_id} reviews a {currency} {amount} transaction for synthetic customer {customer_id}."

    @staticmethod
    def _supporting_evidence(state: InvestigationState, indicators: list[dict]) -> list[str]:
        evidence = [indicator["description"] for indicator in indicators]
        similar_cases = state.outputs.get("HistoricalCaseAgent", {}).get("similar_cases", [])
        if similar_cases:
            evidence.append("Similar historical synthetic cases were found with overlapping risk indicators.")
        return evidence

    @staticmethod
    def _reducing_evidence(state: InvestigationState) -> list[str]:
        reducing = []
        device = state.case.get("device")
        if device and device["trusted"]:
            reducing.append("Device is marked trusted for this synthetic customer.")
        if state.case.get("historical_cases"):
            reducing.append("Prior synthetic history includes customer-confirmed activity.")
        return reducing

    @staticmethod
    def _missing_evidence(state: InvestigationState) -> list[str]:
        missing = []
        if not state.case.get("beneficiary"):
            missing.append("Beneficiary profile is not available for this transaction.")
        if not state.outputs.get("PolicyRagAgent", {}).get("policy_references"):
            missing.append("No matching policy reference was retrieved.")
        return missing
