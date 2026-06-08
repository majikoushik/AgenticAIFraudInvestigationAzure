import logging
from datetime import UTC, datetime, timedelta

from app.security.azure_identity_client import get_azure_credential
from app.security.secret_config import SecretConfig, secret_config
from app.security.secret_provider import BaseSecretProvider

logger = logging.getLogger(__name__)


class KeyVaultSecretProvider(BaseSecretProvider):
    def __init__(self, config: SecretConfig | None = None, client=None, cache_ttl_seconds: int = 300) -> None:
        self.config = config or secret_config
        self._client = client
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self.cache: dict[str, tuple[str, datetime]] = {}

    def get_secret(self, logical_key: str) -> str | None:
        secret_name = self.config.get_secret_name(logical_key)
        return self.get_secret_by_name(secret_name) if secret_name else None

    def get_secret_by_name(self, secret_name: str | None) -> str | None:
        if not secret_name:
            return None
        cached = self.cache.get(secret_name)
        if cached and datetime.now(UTC) - cached[1] < self.cache_ttl:
            return cached[0]
        client = self._get_client()
        if client is None:
            return None
        try:
            value = client.get_secret(secret_name).value
            self.cache[secret_name] = (value, datetime.now(UTC))
            return value
        except Exception:
            logger.warning("Key Vault secret load failed for configured secret name.")
            return None

    def is_available(self) -> bool:
        return bool(self.config.key_vault_enabled and self.config.key_vault_uri and self._get_client())

    def provider_name(self) -> str:
        return "key_vault"

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.config.key_vault_enabled or not self.config.key_vault_uri:
            return None
        try:
            from azure.keyvault.secrets import SecretClient

            credential = get_azure_credential()
            if credential is None:
                return None
            self._client = SecretClient(vault_url=self.config.key_vault_uri, credential=credential)
            return self._client
        except Exception:
            logger.warning("Key Vault client unavailable; check Azure SDK and identity configuration.")
            return None
