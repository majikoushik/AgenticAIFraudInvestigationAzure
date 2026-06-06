import os
from typing import Any

from agents.llm.base_llm_client import BaseLLMClient


class FoundryAgentClient(BaseLLMClient):
    provider_name = "foundry_agent_service"

    def __init__(self) -> None:
        self.project_endpoint = os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT", "")
        self.agent_id = os.getenv("AZURE_AI_FOUNDRY_AGENT_ID", "")

    def is_available(self) -> bool:
        return bool(self.project_endpoint and self.agent_id)

    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        del prompt, system_prompt
        return "Azure AI Foundry Agent Service integration is a future-ready placeholder for this MVP."

    def generate_json(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        del prompt, system_prompt
        return {
            "provider": self.provider_name,
            "available": self.is_available(),
            "message": "Azure AI Foundry Agent Service integration is not implemented in this MVP.",
        }
