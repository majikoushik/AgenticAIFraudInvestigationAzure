from app.security.key_vault_secret_provider import KeyVaultSecretProvider
from app.security.secret_config import SecretConfig


class FakeSecret:
    value = "fake-value"


class FakeClient:
    def get_secret(self, secret_name: str) -> FakeSecret:
        return FakeSecret()


def test_key_vault_unavailable_without_uri() -> None:
    provider = KeyVaultSecretProvider(SecretConfig(key_vault_enabled=True, key_vault_uri=""))
    assert provider.is_available() is False


def test_key_vault_provider_handles_mocked_client() -> None:
    provider = KeyVaultSecretProvider(SecretConfig(key_vault_enabled=True, key_vault_uri="https://example.vault.azure.net/"), client=FakeClient())
    assert provider.get_secret_by_name("name") == "fake-value"
    assert provider.provider_name() == "key_vault"
