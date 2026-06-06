from typing import Any

from agents.agents.base_agent import BaseAgent
from agents.orchestration.state_manager import InvestigationState


class CaseIntakeAgent(BaseAgent):
    name = "CaseIntakeAgent"
    required_fields = [
        "metadata.case_id",
        "customer.customer_id",
        "suspicious_transaction.transaction_id",
        "current_status",
    ]

    def run(self, state: InvestigationState) -> dict[str, Any]:
        missing_fields = [
            field_path for field_path in self.required_fields if self._get_nested(state.case, field_path) is None
        ]

        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
        }

    @staticmethod
    def _get_nested(data: dict[str, Any], field_path: str) -> Any:
        value: Any = data
        for key in field_path.split("."):
            if not isinstance(value, dict) or key not in value:
                return None
            value = value[key]
        return value
