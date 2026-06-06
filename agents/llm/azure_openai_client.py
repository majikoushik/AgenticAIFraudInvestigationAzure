import json
import logging
import os
from typing import Any

from agents.llm.base_llm_client import BaseLLMClient

logger = logging.getLogger(__name__)


class AzureOpenAIClient(BaseLLMClient):
    provider_name = "azure_openai"

    def __init__(self, timeout_seconds: float = 30.0, max_retries: int = 2) -> None:
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def is_available(self) -> bool:
        return bool(self.endpoint and self.api_key and self.api_version and self.deployment)

    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        if not self.is_available():
            logger.warning("Azure OpenAI config missing; cannot generate text.")
            return "Azure OpenAI is not configured. Falling back to local deterministic mode is required."

        try:
            client = self._create_client()
            logger.info("Calling Azure OpenAI chat deployment.", extra={"provider": self.provider_name})
            response = client.chat.completions.create(
                model=self.deployment,
                messages=self._messages(prompt, system_prompt),
                temperature=0.1,
                timeout=self.timeout_seconds,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # pragma: no cover - exercised only with Azure SDK/config
            logger.exception("Azure OpenAI text generation failed.", extra={"provider": self.provider_name})
            return f"Azure OpenAI call failed: {exc}"

    def generate_json(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        text = self.generate_text(prompt, system_prompt)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Azure OpenAI returned non-JSON output.", extra={"provider": self.provider_name})
            return {
                "provider": self.provider_name,
                "raw_text": text,
                "parse_error": "Azure OpenAI response was not valid JSON.",
            }

    def _create_client(self):
        try:
            from openai import AzureOpenAI
        except ImportError as exc:  # pragma: no cover - depends on optional package
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
