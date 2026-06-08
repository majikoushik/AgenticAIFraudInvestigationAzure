from dataclasses import dataclass

from app.config import settings


SECRET_NAME_MAP = {
    "AZURE_OPENAI_ENDPOINT": "azure_openai_endpoint_secret_name",
    "AZURE_OPENAI_API_KEY": "azure_openai_api_key_secret_name",
    "AZURE_SEARCH_ENDPOINT": "azure_search_endpoint_secret_name",
    "AZURE_SEARCH_ADMIN_KEY": "azure_search_admin_key_secret_name",
    "AZURE_SEARCH_QUERY_KEY": "azure_search_query_key_secret_name",
    "COSMOS_CONNECTION_STRING": "cosmos_connection_string_secret_name",
    "STORAGE_CONNECTION_STRING": "storage_connection_string_secret_name",
    "SERVICE_BUS_CONNECTION_STRING": "service_bus_connection_string_secret_name",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": "applicationinsights_connection_string_secret_name",
    "TEAMS_WEBHOOK_URL": "teams_webhook_url_secret_name",
    "SMTP_PASSWORD": "smtp_password_secret_name",
}


@dataclass(frozen=True)
class SecretConfig:
    deployment_mode: str = settings.deployment_mode
    use_managed_identity: bool = settings.use_managed_identity
    azure_client_id: str = settings.azure_client_id
    key_vault_enabled: bool = settings.key_vault_enabled
    key_vault_uri: str = settings.key_vault_uri
    key_vault_secret_prefix: str = settings.key_vault_secret_prefix
    secret_provider: str = settings.secret_provider
    private_endpoints_enabled: bool = settings.private_endpoints_enabled
    disable_public_network_access: bool = settings.disable_public_network_access

    def is_production_mode(self) -> bool:
        return self.deployment_mode.lower() in {"prod", "production"}

    def get_secret_name(self, logical_secret_key: str) -> str | None:
        attr = SECRET_NAME_MAP.get(logical_secret_key.upper())
        return getattr(settings, attr) if attr else None

    def safe_summary(self) -> dict:
        return {
            "deployment_mode": self.deployment_mode,
            "use_managed_identity": self.use_managed_identity,
            "managed_identity_configured": bool(self.azure_client_id) or self.use_managed_identity,
            "key_vault_enabled": self.key_vault_enabled,
            "key_vault_configured": bool(self.key_vault_uri),
            "secret_provider": self.secret_provider,
            "private_endpoints_enabled": self.private_endpoints_enabled,
            "disable_public_network_access": self.disable_public_network_access,
            "configured_secret_names": {key: self.get_secret_name(key) for key in SECRET_NAME_MAP},
        }


secret_config = SecretConfig()
