import logging
import os

from agents.llm.azure_openai_client import AzureOpenAIClient
from agents.llm.base_llm_client import BaseLLMClient
from agents.llm.foundry_agent_client import FoundryAgentClient
from agents.llm.local_llm_client import LocalLLMClient

logger = logging.getLogger(__name__)


class LLMClientFactory:
    @staticmethod
    def create() -> BaseLLMClient:
        if os.getenv("USE_AZURE_AI_FOUNDRY_AGENT_SERVICE", "false").lower() == "true":
            client = FoundryAgentClient()
            if client.is_available():
                logger.info("Using Azure AI Foundry Agent Service client.")
                return client
            logger.warning("Foundry Agent Service requested but not configured. Falling back to local mode.")

        if os.getenv("USE_AZURE_OPENAI", "false").lower() == "true":
            client = AzureOpenAIClient()
            if client.is_available():
                logger.info("Using Azure OpenAI client.")
                return client
            logger.warning("Azure OpenAI requested but not configured. Falling back to local mode.")

        logger.info("Using local deterministic LLM client.")
        return LocalLLMClient()


def current_agent_mode() -> str:
    if os.getenv("USE_AZURE_AI_FOUNDRY_AGENT_SERVICE", "false").lower() == "true":
        client = FoundryAgentClient()
        return "foundry_agent_service" if client.is_available() else "local"
    if os.getenv("USE_AZURE_OPENAI", "false").lower() == "true":
        client = AzureOpenAIClient()
        return "azure_openai" if client.is_available() else "local"
    return "local"
