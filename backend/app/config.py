from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fraud-investigation-backend"
    environment: str = "local"
    log_level: str = "info"
    log_format: str = "json"
    synthetic_data_path: str = "../data/synthetic"
    ai_provider: str = "local"
    ai_provider_allow_fallback: bool = True
    use_azure_openai: bool = False
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_chat_deployment: str = "gpt-4o-mini"
    azure_openai_reasoning_deployment: str = ""
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_request_timeout_seconds: int = 60
    azure_openai_max_retries: int = 3
    azure_openai_temperature: float = 0.2
    azure_openai_max_tokens: int = 2000
    use_azure_ai_foundry_agent_service: bool = False
    azure_ai_foundry_project_endpoint: str = ""
    azure_ai_foundry_agent_id: str = ""
    azure_ai_foundry_connection_name: str = ""
    azure_ai_foundry_thread_id: str = ""
    llm_enable_json_mode: bool = True
    llm_enable_streaming: bool = False
    llm_log_prompts: bool = False
    llm_log_responses: bool = False
    ai_safety_require_human_review: bool = True
    ai_safety_require_citations: bool = True
    ai_safety_max_recommendation_confidence: str = "HIGH"
    auth_mode: str = "local"
    entra_tenant_id: str = ""
    entra_client_id: str = ""
    entra_api_audience: str = ""
    entra_authority: str = ""
    entra_allow_default_role: bool = False
    azure_search_endpoint: str = ""
    azure_ai_search_endpoint: str = ""
    observability_enabled: bool = True
    observability_mode: str = "local"
    applicationinsights_connection_string: str = ""
    applicationinsights_instrumentation_key: str = ""
    telemetry_service_name: str = "fraud-investigation-platform"
    telemetry_environment: str = "local"
    telemetry_sample_rate: float = 1.0
    telemetry_enable_api: bool = True
    telemetry_enable_agent: bool = True
    telemetry_enable_rag: bool = True
    telemetry_enable_llm: bool = True
    telemetry_enable_business: bool = True
    telemetry_enable_security: bool = True
    telemetry_log_prompts: bool = False
    telemetry_log_responses: bool = False
    telemetry_log_pii: bool = False
    token_cost_input_per_1k: float = 0.0
    token_cost_output_per_1k: float = 0.0
    currency: str = "USD"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


def get_synthetic_data_path() -> Path:
    configured_path = Path(settings.synthetic_data_path)
    if configured_path.is_absolute():
        return configured_path

    backend_dir = Path(__file__).resolve().parents[1]
    return (backend_dir / configured_path).resolve()
