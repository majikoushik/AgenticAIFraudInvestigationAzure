from typing import Any
import logging
from time import perf_counter

from app.core.constants import AuditEventType
from app.services.audit_service import audit_service
from agents.orchestration.agent_registry import AgentRegistry
from agents.orchestration.state_manager import StateManager

logger = logging.getLogger(__name__)


class FraudInvestigationOrchestrator:
    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry()

    def investigate(self, case: dict[str, Any]) -> dict[str, Any]:
        state_manager = StateManager(case)
        case_id = case.get("metadata", {}).get("case_id")

        for agent in self.registry.build_default_agents():
            logger.info("Agent started.", extra={"agent": agent.name})
            audit_service.create_agent_execution_event(
                case_id=case_id,
                event_type=AuditEventType.AGENT_EXECUTION_STARTED,
                agent_name=agent.name,
            )
            started = perf_counter()
            try:
                output = agent.run(state_manager.state)
            except Exception as exc:
                audit_service.create_agent_execution_event(
                    case_id=case_id,
                    event_type=AuditEventType.AGENT_EXECUTION_FAILED,
                    agent_name=agent.name,
                    error_message=str(exc),
                )
                raise
            state_manager.record_agent_output(agent.name, output)
            duration_ms = round((perf_counter() - started) * 1000, 2)
            audit_service.create_agent_execution_event(
                case_id=case_id,
                event_type=AuditEventType.AGENT_EXECUTION_COMPLETED,
                agent_name=agent.name,
                metadata={
                    "duration_ms": duration_ms,
                    "output_keys": sorted(output.keys()),
                },
            )
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
