from pydantic import BaseModel


class AgentConfigResponse(BaseModel):
    use_azure_openai: bool
    chat_deployment_configured: bool
    use_foundry_agent_service: bool
    mode: str
