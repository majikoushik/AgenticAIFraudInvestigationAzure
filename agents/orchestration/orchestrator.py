from typing import Any
import logging

from agents.orchestration.agent_registry import AgentRegistry
from agents.orchestration.state_manager import StateManager

logger = logging.getLogger(__name__)


class FraudInvestigationOrchestrator:
    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry()

    def investigate(self, case: dict[str, Any]) -> dict[str, Any]:
        state_manager = StateManager(case)

        for agent in self.registry.build_default_agents():
            logger.info("Agent started.", extra={"agent": agent.name})
            output = agent.run(state_manager.state)
            state_manager.record_agent_output(agent.name, output)
            logger.info("Agent completed.", extra={"agent": agent.name})

        outputs = state_manager.state.outputs
        summary = outputs["CaseSummaryAgent"]
        reviewer_validation = outputs["ReviewerAgent"]

        return {
            "case_id": case["metadata"]["case_id"],
            "agent_trace": state_manager.state.agent_trace,
            "risk_indicators": summary["key_risk_indicators"],
            "policy_references": outputs["PolicyRagAgent"]["policy_references"],
            "similar_cases": outputs["HistoricalCaseAgent"]["similar_cases"],
            "investigation_summary": summary,
            "reviewer_validation": reviewer_validation,
            "human_review_required": True,
        }
