from app.security.azure_identity_client import credential_available
from app.security.secret_config import SECRET_NAME_MAP, secret_config
from app.security.secure_config_loader import SecureConfigLoader


class SecurityHealthService:
    REQUIRED_LOGICAL_SECRETS = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_SEARCH_QUERY_KEY",
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "TEAMS_WEBHOOK_URL",
        "SMTP_PASSWORD",
    ]

    def __init__(self, loader: SecureConfigLoader | None = None) -> None:
        self.loader = loader or SecureConfigLoader()

    def get_security_health(self) -> dict:
        required = self._required_secret_status()
        warnings = self._warnings(required)
        status = "ok"
        if warnings:
            status = "degraded"
        if secret_config.is_production_mode() and any(value == "missing" for value in required.values()):
            status = "unhealthy"
        return {
            "deployment_mode": secret_config.deployment_mode,
            "secret_provider": self.loader.provider.provider_name(),
            "key_vault_enabled": secret_config.key_vault_enabled,
            "key_vault_configured": bool(secret_config.key_vault_uri),
            "managed_identity_enabled": secret_config.use_managed_identity,
            "managed_identity_configured": credential_available(),
            "private_endpoints_enabled": secret_config.private_endpoints_enabled,
            "public_network_access_disabled": secret_config.disable_public_network_access,
            "required_secrets": required,
            "warnings": warnings,
            "status": status,
        }

    def _required_secret_status(self) -> dict[str, str]:
        statuses = {}
        for logical_key in self.REQUIRED_LOGICAL_SECRETS:
            if self._managed_identity_replaces(logical_key):
                statuses[logical_key] = "managed_identity"
                continue
            if logical_key not in SECRET_NAME_MAP:
                statuses[logical_key] = "not_required"
                continue
            value = self.loader.get_secret(logical_key, required=False)
            statuses[logical_key] = "configured" if value else "missing"
        return statuses

    @staticmethod
    def _managed_identity_replaces(logical_key: str) -> bool:
        return secret_config.use_managed_identity and logical_key in {"AZURE_OPENAI_API_KEY", "AZURE_SEARCH_QUERY_KEY"}

    @staticmethod
    def _warnings(required: dict[str, str]) -> list[str]:
        warnings = []
        if secret_config.is_production_mode() and not secret_config.key_vault_enabled:
            warnings.append("Production mode should enable Key Vault.")
        if secret_config.key_vault_enabled and not secret_config.key_vault_uri:
            warnings.append("Key Vault is enabled but KEY_VAULT_URI is missing.")
        if secret_config.is_production_mode() and not secret_config.use_managed_identity:
            warnings.append("Production mode should use managed identity.")
        if secret_config.is_production_mode() and not secret_config.private_endpoints_enabled:
            warnings.append("Production mode should enable private endpoints where practical.")
        if any(value == "missing" for value in required.values()):
            warnings.append("One or more configured secrets are missing.")
        return warnings


security_health_service = SecurityHealthService()
