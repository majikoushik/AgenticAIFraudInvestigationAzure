import logging
import os
from typing import Any

from app.security.environment_secret_provider import EnvironmentSecretProvider
from app.security.key_vault_secret_provider import KeyVaultSecretProvider
from app.security.secret_config import SecretConfig, secret_config
from app.security.secret_redaction import redact_config_dict

logger = logging.getLogger(__name__)


class SecureConfigLoader:
    def __init__(self, config: SecretConfig | None = None, provider=None) -> None:
        self.config = config or secret_config
        if provider is not None:
            self.provider = provider
        elif self.config.secret_provider == "key_vault" or self.config.key_vault_enabled:
            self.provider = KeyVaultSecretProvider(self.config)
        else:
            self.provider = EnvironmentSecretProvider(self.config)

    def get_value(self, key: str, default: Any = None) -> Any:
        return os.getenv(key, default)

    def get_secret(self, logical_key: str, required: bool = False) -> str | None:
        value = self.provider.get_secret(logical_key)
        if value is None and required:
            message = f"Required secret {logical_key} is not configured."
            if self.config.is_production_mode():
                raise RuntimeError(message)
            logger.warning(message)
        return value

    def get_safe_config_summary(self) -> dict:
        return redact_config_dict({
            **self.config.safe_summary(),
            "provider_available": self.provider.is_available(),
            "provider_name": self.provider.provider_name(),
        })


secure_config_loader = SecureConfigLoader()
