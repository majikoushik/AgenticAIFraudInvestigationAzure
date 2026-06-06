from agents.agents.base_agent import BaseAgent
from agents.agents.beneficiary_risk_agent import BeneficiaryRiskAgent
from agents.agents.case_intake_agent import CaseIntakeAgent
from agents.agents.case_summary_agent import CaseSummaryAgent
from agents.agents.customer_profile_agent import CustomerProfileAgent
from agents.agents.device_location_agent import DeviceLocationAgent
from agents.agents.historical_case_agent import HistoricalCaseAgent
from agents.agents.policy_rag_agent import PolicyRagAgent
from agents.agents.reviewer_agent import ReviewerAgent
from agents.agents.transaction_pattern_agent import TransactionPatternAgent


class AgentRegistry:
    def build_default_agents(self) -> list[BaseAgent]:
        return [
            CaseIntakeAgent(),
            CustomerProfileAgent(),
            TransactionPatternAgent(),
            DeviceLocationAgent(),
            BeneficiaryRiskAgent(),
            PolicyRagAgent(),
            HistoricalCaseAgent(),
            CaseSummaryAgent(),
            ReviewerAgent(),
        ]
