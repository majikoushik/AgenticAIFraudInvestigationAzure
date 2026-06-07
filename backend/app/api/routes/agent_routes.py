from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.config import settings
from app.schemas.agent_config_schema import AgentConfigResponse

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
