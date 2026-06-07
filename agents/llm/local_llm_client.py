import json
from time import perf_counter
from typing import Any

from agents.llm.base_llm_client import BaseLLMClient, llm_response
from agents.llm.token_usage import build_usage
from agents.observability.llm_telemetry import estimate_cost, track_llm_event

try:
    from app.observability import telemetry_events
except Exception:  # pragma: no cover - agents can run outside backend
    telemetry_events = None


class LocalLLMClient(BaseLLMClient):
    provider_name = "local"
    model_name = "local-deterministic"

    def is_available(self) -> bool:
        return True

    def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        del system_prompt, metadata
        started = perf_counter()
        if telemetry_events:
            track_llm_event(telemetry_events.LLM_CALL_STARTED, {"provider": self.provider_name, "json_mode": False})
        content = f"Local deterministic response generated from prompt context: {prompt[:500]}"
        response = llm_response(
            provider=self.provider_name,
            model=self.model_name,
            content=content,
            usage=build_usage(prompt, content),
            latency_ms=(perf_counter() - started) * 1000,
            finish_reason="stop",
        )
        if telemetry_events:
            track_llm_event(telemetry_events.LLM_CALL_COMPLETED, {"provider": self.provider_name, "finish_reason": "stop", "prompt_redacted": True, "response_redacted": True}, {"latency_ms": response["latency_ms"]})
        return response

    def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        json_schema: dict | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        del system_prompt, json_schema, metadata
        started = perf_counter()
        if telemetry_events:
            track_llm_event(telemetry_events.LLM_CALL_STARTED, {"provider": self.provider_name, "json_mode": True})
        try:
            payload = json.loads(prompt)
            if isinstance(payload, dict) and "required_schema" in payload:
                payload = self._from_required_schema(payload["required_schema"])
        except json.JSONDecodeError:
            payload = {"summary": f"Local deterministic response generated from prompt context: {prompt[:500]}"}
        response = llm_response(
            provider=self.provider_name,
            model=self.model_name,
            content=json.dumps(payload, ensure_ascii=True),
            json_payload=payload,
            usage=build_usage(prompt, json.dumps(payload, ensure_ascii=True)),
            latency_ms=(perf_counter() - started) * 1000,
            finish_reason="stop",
        )
        if telemetry_events:
            cost = estimate_cost(0, 0)
            track_llm_event(telemetry_events.LLM_CALL_COMPLETED, {"provider": self.provider_name, "finish_reason": "stop", "prompt_redacted": True, "response_redacted": True}, {"latency_ms": response["latency_ms"]})
            track_llm_event(telemetry_events.LLM_TOKEN_USAGE_RECORDED, {"provider": self.provider_name}, response["usage"])
            track_llm_event(telemetry_events.LLM_COST_ESTIMATED, {"provider": self.provider_name, "currency": "USD"}, {"estimated_cost": cost})
        return response

    def _from_required_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        if "case_overview" in schema or "recommended_action" in schema or "is_evidence_supported" in schema:
            payload = dict(schema)
            payload["human_review_required"] = True
            return payload
        payload = {}
        for key, value in schema.items():
            if key == "human_review_required":
                payload[key] = True
            elif isinstance(value, bool):
                payload[key] = value
            elif isinstance(value, list):
                payload[key] = []
            elif isinstance(value, dict):
                payload[key] = {}
            elif "confidence" in key:
                payload[key] = "MEDIUM"
            elif "recommended_action" in key:
                payload[key] = "HOLD"
            else:
                payload[key] = str(value) if value else ""
        return payload
