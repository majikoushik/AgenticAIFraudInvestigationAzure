import logging
import os

from app.security.secret_config import SecretConfig, secret_config
from app.security.secret_provider import BaseSecretProvider

logger = logging.getLogger(__name__)


class EnvironmentSecretProvider(BaseSecretProvider):
    def __init__(self, config: SecretConfig | None = None) -> None:
        self.config = config or secret_config

    def get_secret(self, logical_key: str) -> str | None:
        if self.config.is_production_mode():
            logger.warning("Environment secret provider is being used in production mode for a sensitive key.")
        return os.getenv(logical_key)

    def get_secret_by_name(self, secret_name: str) -> str | None:
        if self.config.is_production_mode():
            logger.warning("Environment secret provider is being used in production mode for a secret name.")
        return os.getenv(secret_name)

    def is_available(self) -> bool:
        return True

    def provider_name(self) -> str:
        return "environment"
