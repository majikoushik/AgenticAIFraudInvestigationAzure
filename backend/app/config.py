from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fraud-investigation-backend"
    environment: str = "local"
    log_level: str = "info"
    synthetic_data_path: str = "../data/synthetic"
    use_azure_openai: bool = False
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_chat_deployment: str = "gpt-4o-mini"
    use_azure_ai_foundry_agent_service: bool = False
    azure_ai_foundry_project_endpoint: str = ""
    azure_ai_foundry_agent_id: str = ""

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
