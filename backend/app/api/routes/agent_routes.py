from pathlib import Path
import sys

from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.config import settings
from app.schemas.agent_config_schema import AgentConfigResponse, AgentProviderResponse


def _ensure_project_root_on_path() -> None:
    project_root = Path(__file__).resolve().parents[4]
    project_root_text = str(project_root)
    if project_root_text not in sys.path:
        sys.path.append(project_root_text)


_ensure_project_root_on_path()

from agents.llm.azure_openai_client import AzureOpenAIClient
from agents.llm.foundry_agent_client import FoundryAgentClient
from agents.llm.llm_client_factory import LLMClientFactory, current_requested_provider
from agents.llm.local_llm_client import LocalLLMClient

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/config", response_model=AgentConfigResponse)
def get_agent_config(current_user: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> AgentConfigResponse:
    del current_user
    foundry_configured = bool(settings.azure_ai_foundry_project_endpoint and settings.azure_ai_foundry_agent_id)
    azure_openai_configured = bool(settings.azure_openai_endpoint and settings.azure_openai_chat_deployment)

    if settings.use_azure_ai_foundry_agent_service and foundry_configured:
        mode = "foundry_agent_service"
    elif settings.use_azure_openai and azure_openai_configured:
        mode = "azure_openai"
    else:
        mode = "local"

    return AgentConfigResponse(
        use_azure_openai=settings.use_azure_openai,
        chat_deployment_configured=azure_openai_configured,
        use_foundry_agent_service=settings.use_azure_ai_foundry_agent_service,
        mode=mode,
    )


@router.get("/provider", response_model=AgentProviderResponse)
def get_agent_provider(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_CASE_DETAILS))) -> AgentProviderResponse:
    del current_user
    requested = current_requested_provider()
    if requested == "azure_openai":
        provider_client = AzureOpenAIClient()
    elif requested == "foundry_agent_service":
        provider_client = FoundryAgentClient()
    else:
        provider_client = LocalLLMClient()
    selected = LLMClientFactory.create()
    return AgentProviderResponse(
        ai_provider=selected.get_provider_name(),
        provider_available=provider_client.is_available(),
        fallback_enabled=settings.ai_provider_allow_fallback,
        json_mode_enabled=settings.llm_enable_json_mode,
        prompt_logging_enabled=settings.llm_log_prompts,
        response_logging_enabled=settings.llm_log_responses,
        human_review_required=settings.ai_safety_require_human_review,
    )
