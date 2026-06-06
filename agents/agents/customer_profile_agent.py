from agents.agents.base_agent import BaseAgent
from agents.orchestration.state_manager import InvestigationState


class CustomerProfileAgent(BaseAgent):
    name = "CustomerProfileAgent"

    def run(self, state: InvestigationState) -> dict:
        transaction = state.case["suspicious_transaction"]
        customer = state.case["customer"]
        amount = float(transaction["amount"])
        average_amount = float(customer.get("average_transaction_amount", 500.0))
        ratio = round(amount / average_amount, 2) if average_amount else 0.0
        unusual = ratio >= 3.0

        indicator = {
            "code": "UNUSUAL_CUSTOMER_AMOUNT",
            "description": f"Transaction amount is {ratio}x the synthetic customer average.",
            "severity": "high" if ratio >= 5.0 else "medium",
        }

        return {
            "average_transaction_amount": average_amount,
            "transaction_amount": amount,
            "amount_to_average_ratio": ratio,
            "is_unusual_amount": unusual,
            "risk_indicators": [indicator] if unusual else [],
        }
