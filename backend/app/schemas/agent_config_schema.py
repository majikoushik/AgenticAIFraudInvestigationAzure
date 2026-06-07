from pydantic import BaseModel


class AgentConfigResponse(BaseModel):
    use_azure_openai: bool
    chat_deployment_configured: bool
    use_foundry_agent_service: bool
    mode: str


class AgentProviderResponse(BaseModel):
    ai_provider: str
    provider_available: bool
    fallback_enabled: bool
    json_mode_enabled: bool
    prompt_logging_enabled: bool
    response_logging_enabled: bool
    human_review_required: bool
