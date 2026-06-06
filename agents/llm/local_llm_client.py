import json
from typing import Any

from agents.llm.base_llm_client import BaseLLMClient


class LocalLLMClient(BaseLLMClient):
    provider_name = "local"

    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        del system_prompt
        return f"Local deterministic response generated from prompt context: {prompt[:500]}"

    def generate_json(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        del system_prompt
        try:
            return json.loads(prompt)
        except json.JSONDecodeError:
            return {
                "provider": self.provider_name,
                "summary": self.generate_text(prompt),
            }

    def is_available(self) -> bool:
        return True
