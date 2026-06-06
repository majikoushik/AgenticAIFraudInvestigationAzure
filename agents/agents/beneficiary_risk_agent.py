from agents.agents.base_agent import BaseAgent
from agents.orchestration.state_manager import InvestigationState


class BeneficiaryRiskAgent(BaseAgent):
    name = "BeneficiaryRiskAgent"

    def run(self, state: InvestigationState) -> dict:
        transaction = state.case["suspicious_transaction"]
        beneficiary = state.case.get("beneficiary")
        indicators = []

        if not beneficiary:
            return {"beneficiary_present": False, "risk_indicators": []}

        is_new = beneficiary["first_seen"] == transaction["timestamp"][:10]
        if is_new:
            indicators.append(
                {
                    "code": "NEW_BENEFICIARY",
                    "description": "Beneficiary was first seen on the alert transaction date.",
                    "severity": "medium",
                }
            )

        if "high-value" in beneficiary.get("risk_note", "").lower() or "cross-border" in beneficiary.get("risk_note", "").lower():
            indicators.append(
                {
                    "code": "BENEFICIARY_RISK_NOTE",
                    "description": beneficiary["risk_note"],
                    "severity": "medium",
                }
            )

        return {
            "beneficiary_present": True,
            "beneficiary_id": beneficiary["beneficiary_id"],
            "is_new_beneficiary": is_new,
            "risk_indicators": indicators,
        }
