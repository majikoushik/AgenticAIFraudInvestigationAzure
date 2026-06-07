from typing import Any
import logging
from time import perf_counter

from app.core.constants import AuditEventType
from app.services.audit_service import audit_service
from agents.llm.llm_client_factory import LLMClientFactory
from agents.llm.token_usage import add_usage
from agents.observability.agent_telemetry import track_agent_event
from agents.orchestration.agent_registry import AgentRegistry
from agents.orchestration.state_manager import StateManager
from agents.safety.guardrail_engine import GuardrailEngine
from app.observability import telemetry_events as telemetry_events

logger = logging.getLogger(__name__)


class FraudInvestigationOrchestrator:
    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry()
        self.guardrails = GuardrailEngine()

    def investigate(self, case: dict[str, Any]) -> dict[str, Any]:
        state_manager = StateManager(case)
        case_id = case.get("metadata", {}).get("case_id")
        provider_client = LLMClientFactory.create()
        ai_provider = provider_client.get_provider_name()
        audit_service.record_event(
            case_id=case_id,
            event_type=AuditEventType.AI_PROVIDER_SELECTED,
            actor="system",
            actor_role="SYSTEM",
            metadata={"provider": ai_provider, "fallback_enabled": True},
        )

        for agent in self.registry.build_default_agents():
            logger.info("Agent started.", extra={"agent": agent.name})
            track_agent_event(telemetry_events.AGENT_EXECUTION_STARTED, {"case_id": case_id, "agent_name": agent.name, "ai_provider": ai_provider})
            audit_service.create_agent_execution_event(
                case_id=case_id,
                event_type=AuditEventType.AGENT_EXECUTION_STARTED,
                agent_name=agent.name,
            )
            started = perf_counter()
            try:
                output = agent.run(state_manager.state)
            except Exception as exc:
                track_agent_event(telemetry_events.AGENT_EXECUTION_FAILED, {"case_id": case_id, "agent_name": agent.name, "error_type": type(exc).__name__})
                audit_service.create_agent_execution_event(
                    case_id=case_id,
                    event_type=AuditEventType.AGENT_EXECUTION_FAILED,
                    agent_name=agent.name,
                    error_message=str(exc),
                )
                raise
            state_manager.record_agent_output(agent.name, output)
            duration_ms = round((perf_counter() - started) * 1000, 2)
            fallback_used = bool(output.get("llm_response_metadata", {}).get("fallback_used")) if isinstance(output, dict) else False
            if fallback_used:
                track_agent_event(telemetry_events.AGENT_FALLBACK_USED, {"case_id": case_id, "agent_name": agent.name, "ai_provider": ai_provider})
            track_agent_event(
                telemetry_events.AGENT_EXECUTION_COMPLETED,
                {
                    "case_id": case_id,
                    "agent_name": agent.name,
                    "ai_provider": ai_provider,
                    "fallback_used": fallback_used,
                    "human_review_required": bool(output.get("human_review_required", True)) if isinstance(output, dict) else True,
                    "safety_flag_count": len(output.get("safety_flags", [])) if isinstance(output, dict) else 0,
                    "validation_passed": output.get("validation_result", {}).get("passed") if isinstance(output, dict) else None,
                    "output_keys": sorted(output.keys()) if isinstance(output, dict) else [],
                },
                {"duration_ms": duration_ms},
            )
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
        llm_metadata = [
            {"agent_name": agent_name, **output.get("llm_response_metadata", {})}
            for agent_name, output in outputs.items()
            if isinstance(output, dict) and output.get("llm_response_metadata")
        ]
        token_usage = add_usage(llm_metadata)
        latency_ms = round(sum(float(item.get("latency_ms", 0) or 0) for item in llm_metadata), 2)
        safety_flags = sorted(set(summary.get("safety_flags", []) + reviewer_validation.get("safety_flags", [])))
        validation_result = summary.get("validation_result", self.guardrails.validate_summary(summary, outputs["PolicyRagAgent"]["policy_references"]))
        citations = [
            reference.get("citation", {})
            for reference in outputs["PolicyRagAgent"]["policy_references"]
            if reference.get("citation")
        ]

        return {
            "case_id": case["metadata"]["case_id"],
            "ai_provider": ai_provider,
            "ai_mode": "production" if ai_provider != "local" else "local_deterministic",
            "agent_trace": state_manager.state.agent_trace,
            "token_usage": token_usage,
            "token_usage_records": [
                {
                    "case_id": case["metadata"]["case_id"],
                    "agent_name": item.get("agent_name", "UNKNOWN"),
                    "operation_name": "agent_llm_call",
                    "ai_provider": item.get("provider", ai_provider),
                    "model_or_deployment": item.get("model", ""),
                    "prompt_tokens": item.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": item.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": item.get("usage", {}).get("total_tokens", 0),
                    "latency_ms": item.get("latency_ms", 0),
                    "fallback_used": item.get("fallback_used", False),
                    "success": not bool(item.get("error")),
                    "error_type": item.get("error"),
                }
                for item in llm_metadata
            ],
            "latency_ms": latency_ms,
            "citations": citations,
            "safety_flags": safety_flags,
            "validation_result": validation_result,
            "risk_indicators": summary["key_risk_indicators"],
            "policy_references": outputs["PolicyRagAgent"]["policy_references"],
            "similar_cases": outputs["HistoricalCaseAgent"]["similar_cases"],
            "investigation_summary": summary,
            "reviewer_validation": reviewer_validation,
            "human_review_required": True,
        }
