from agents.agents.base_agent import BaseAgent
from agents.orchestration.state_manager import InvestigationState


class TransactionPatternAgent(BaseAgent):
    name = "TransactionPatternAgent"

    def run(self, state: InvestigationState) -> dict:
        transaction = state.case["suspicious_transaction"]
        beneficiary = state.case.get("beneficiary")
        indicators = []

        if float(transaction["amount"]) >= 5000:
            indicators.append(
                {
                    "code": "HIGH_AMOUNT",
                    "description": "Transaction amount exceeds the MVP high-value threshold.",
                    "severity": "high",
                }
            )

        if transaction["channel"] in {"online_banking", "card_not_present"}:
            indicators.append(
                {
                    "code": "REMOTE_CHANNEL",
                    "description": "Transaction occurred through a remote channel.",
                    "severity": "medium",
                }
            )

        if beneficiary and beneficiary.get("first_seen") == transaction["timestamp"][:10]:
            indicators.append(
                {
                    "code": "NEW_BENEFICIARY_TRANSACTION",
                    "description": "Beneficiary first appeared on the transaction date.",
                    "severity": "medium",
                }
            )

        return {
            "transaction_id": transaction["transaction_id"],
            "checked_dimensions": ["amount", "frequency", "channel", "new_beneficiary"],
            "risk_indicators": indicators,
        }
