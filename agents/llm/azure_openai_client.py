import json
import logging
import os
from time import perf_counter
from typing import Any

from agents.llm.base_llm_client import BaseLLMClient, llm_response
from agents.llm.llm_response_parser import LLMResponseParser
from agents.observability.llm_telemetry import estimate_cost, track_llm_event
from agents.safety.pii_redactor import PiiRedactor

try:
    from app.observability import telemetry_events
except Exception:  # pragma: no cover
    telemetry_events = None

logger = logging.getLogger(__name__)


class AzureOpenAIClient(BaseLLMClient):
    provider_name = "azure_openai"

    def __init__(self) -> None:
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
        self.reasoning_deployment = os.getenv("AZURE_OPENAI_REASONING_DEPLOYMENT", "")
        self.timeout_seconds = float(os.getenv("AZURE_OPENAI_REQUEST_TIMEOUT_SECONDS", "60"))
        self.max_retries = int(os.getenv("AZURE_OPENAI_MAX_RETRIES", "3"))
        self.temperature = float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "2000"))
        self.json_mode_enabled = os.getenv("LLM_ENABLE_JSON_MODE", "true").lower() == "true"
        self.log_prompts = os.getenv("LLM_LOG_PROMPTS", "false").lower() == "true"
        self.log_responses = os.getenv("LLM_LOG_RESPONSES", "false").lower() == "true"
        self.redactor = PiiRedactor()
        self.parser = LLMResponseParser()
        self.model_name = self.deployment

    def is_available(self) -> bool:
        return bool(self.endpoint and self.api_key and self.api_version and self.deployment)

    def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        return self._generate(prompt, system_prompt, metadata=metadata, json_mode=False)

    def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        json_schema: dict | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        del json_schema
        return self._generate(prompt, system_prompt, metadata=metadata, json_mode=self.json_mode_enabled)

    def _generate(self, prompt: str, system_prompt: str | None, metadata: dict | None, json_mode: bool) -> dict[str, Any]:
        del metadata
        started = perf_counter()
        if telemetry_events:
            track_llm_event(telemetry_events.LLM_CALL_STARTED, {"provider": self.provider_name, "deployment": self.deployment, "json_mode": json_mode})
        if not self.is_available():
            response = llm_response(self.provider_name, self.model_name, error="Azure OpenAI configuration is incomplete.", finish_reason="error")
            if telemetry_events:
                track_llm_event(telemetry_events.LLM_CALL_FAILED, {"provider": self.provider_name, "deployment": self.deployment, "error": response["error"]})
            return response

        redacted_prompt = self.redactor.redact_text(prompt)
        redacted_system = self.redactor.redact_text(system_prompt or "") if system_prompt else None
        if telemetry_events and redacted_prompt != prompt:
            track_llm_event(telemetry_events.PII_REDACTION_APPLIED, {"provider": self.provider_name, "prompt_redacted": True})
        if self.log_prompts:
            logger.warning("Redacted LLM prompt logging is enabled for local/dev only.", extra={"provider": self.provider_name, "prompt": redacted_prompt})

        try:
            client = self._create_client()
            kwargs: dict[str, Any] = {
                "model": self.deployment,
                "messages": self._messages(redacted_prompt, redacted_system),
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "timeout": self.timeout_seconds,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""
            if self.log_responses:
                logger.warning("Redacted LLM response logging is enabled for local/dev only.", extra={"provider": self.provider_name, "response": self.redactor.redact_text(content)})
            usage = self._usage(response)
            parsed = self.parser.parse_json(content)["parsed"] if json_mode else {}
            response_payload = llm_response(
                provider=self.provider_name,
                model=self.deployment,
                content=content,
                json_payload=parsed,
                usage=usage,
                latency_ms=(perf_counter() - started) * 1000,
                finish_reason=getattr(response.choices[0], "finish_reason", "unknown") or "unknown",
            )
            if telemetry_events:
                cost = estimate_cost(usage["prompt_tokens"], usage["completion_tokens"])
                track_llm_event(
                    telemetry_events.LLM_CALL_COMPLETED,
                    {"provider": self.provider_name, "deployment": self.deployment, "finish_reason": response_payload["finish_reason"], "prompt_redacted": True, "response_redacted": True},
                    {"latency_ms": response_payload["latency_ms"]},
                )
                track_llm_event(telemetry_events.LLM_TOKEN_USAGE_RECORDED, {"provider": self.provider_name, "deployment": self.deployment}, usage)
                track_llm_event(telemetry_events.LLM_COST_ESTIMATED, {"provider": self.provider_name, "currency": os.getenv("CURRENCY", "USD")}, {"estimated_cost": cost})
            return response_payload
        except Exception as exc:  # pragma: no cover - live SDK path is mocked or disabled in default tests
            logger.exception("Azure OpenAI call failed.", extra={"provider": self.provider_name})
            response_payload = llm_response(
                provider=self.provider_name,
                model=self.deployment,
                latency_ms=(perf_counter() - started) * 1000,
                finish_reason="error",
                error=str(exc),
            )
            if telemetry_events:
                track_llm_event(telemetry_events.LLM_CALL_FAILED, {"provider": self.provider_name, "deployment": self.deployment, "error_type": type(exc).__name__}, {"latency_ms": response_payload["latency_ms"]})
            return response_payload

    def _create_client(self):
        try:
            from openai import AzureOpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("The openai package is required for Azure OpenAI mode.") from exc

        return AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            max_retries=self.max_retries,
        )

    @staticmethod
    def _messages(prompt: str, system_prompt: str | None) -> list[dict[str, str]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    @staticmethod
    def _usage(response) -> dict[str, int]:
        usage = getattr(response, "usage", None)
        return {
            "prompt_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
            "completion_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
            "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
        }
