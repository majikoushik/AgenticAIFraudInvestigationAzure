import os
from time import perf_counter
from typing import Any

from agents.llm.base_llm_client import BaseLLMClient, llm_response
from agents.observability.llm_telemetry import track_llm_event

try:
    from app.observability import telemetry_events
except Exception:  # pragma: no cover
    telemetry_events = None


class FoundryAgentClient(BaseLLMClient):
    provider_name = "foundry_agent_service"

    def __init__(self) -> None:
        self.project_endpoint = os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT", "")
        self.agent_id = os.getenv("AZURE_AI_FOUNDRY_AGENT_ID", "")
        self.connection_name = os.getenv("AZURE_AI_FOUNDRY_CONNECTION_NAME", "")
        self.thread_id = os.getenv("AZURE_AI_FOUNDRY_THREAD_ID", "")
        self.enabled = os.getenv("USE_AZURE_AI_FOUNDRY_AGENT_SERVICE", "false").lower() == "true"
        self.model_name = self.agent_id

    def is_available(self) -> bool:
        return bool(self.enabled and self.project_endpoint and self.agent_id)

    def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        del prompt, system_prompt, metadata
        started = perf_counter()
        if telemetry_events:
            track_llm_event(telemetry_events.LLM_CALL_STARTED, {"provider": self.provider_name, "agent_id": self.agent_id})
        response = llm_response(
            provider=self.provider_name,
            model=self.agent_id,
            content="Azure AI Foundry Agent Service adapter is configured as a future-ready placeholder.",
            latency_ms=(perf_counter() - started) * 1000,
            finish_reason="error",
            error="Foundry Agent Service SDK call is not implemented in this MVP adapter.",
        )
        if telemetry_events:
            track_llm_event(telemetry_events.LLM_CALL_FAILED, {"provider": self.provider_name, "agent_id": self.agent_id, "error": response["error"]}, {"latency_ms": response["latency_ms"]})
        return response

    def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        json_schema: dict | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        response = self.generate_text(prompt, system_prompt, metadata)
        response["json"] = {
            "provider": self.provider_name,
            "available": self.is_available(),
            "message": "Wire Azure AI Foundry Agent Service SDK calls here when enterprise credentials and SDK policy are finalized.",
        }
        return response
