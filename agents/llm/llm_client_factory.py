import os

from agents.llm.azure_openai_client import AzureOpenAIClient
from agents.llm.base_llm_client import BaseLLMClient
from agents.llm.foundry_agent_client import FoundryAgentClient
from agents.llm.llm_errors import LLMConfigurationError
from agents.llm.local_llm_client import LocalLLMClient


class LLMClientFactory:
    @staticmethod
    def create() -> BaseLLMClient:
        provider = current_requested_provider()
        fallback_enabled = os.getenv("AI_PROVIDER_ALLOW_FALLBACK", "true").lower() == "true"

        if provider == "local":
            return LocalLLMClient()
        if provider == "azure_openai":
            return LLMClientFactory._client_or_fallback(AzureOpenAIClient(), fallback_enabled)
        if provider == "foundry_agent_service":
            return LLMClientFactory._client_or_fallback(FoundryAgentClient(), fallback_enabled)
        raise LLMConfigurationError(f"Unsupported AI_PROVIDER value: {provider}")

    @staticmethod
    def _client_or_fallback(client: BaseLLMClient, fallback_enabled: bool) -> BaseLLMClient:
        if client.is_available():
            return client
        if fallback_enabled:
            fallback = LocalLLMClient()
            fallback.provider_name = "local"
            return fallback
        raise LLMConfigurationError(f"AI provider {client.get_provider_name()} is not configured and fallback is disabled.")


def current_requested_provider() -> str:
    provider = os.getenv("AI_PROVIDER", "").strip().lower()
    if provider:
        return provider
    if os.getenv("USE_AZURE_AI_FOUNDRY_AGENT_SERVICE", "false").lower() == "true":
        return "foundry_agent_service"
    if os.getenv("USE_AZURE_OPENAI", "false").lower() == "true":
        return "azure_openai"
    return "local"


def current_agent_mode() -> str:
    return LLMClientFactory.create().get_provider_name()
