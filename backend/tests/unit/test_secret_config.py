from app.security.secret_config import SecretConfig


def test_secret_config_safe_summary_does_not_expose_values() -> None:
    config = SecretConfig(key_vault_enabled=True, key_vault_uri="https://example.vault.azure.net/", secret_provider="key_vault")
    summary = config.safe_summary()
    assert summary["key_vault_enabled"] is True
    assert "fraud-ai-azure-openai-api-key" in summary["configured_secret_names"].values()
    assert "secret_values" not in summary


def test_secret_config_get_secret_name() -> None:
    assert SecretConfig().get_secret_name("AZURE_OPENAI_API_KEY") == "fraud-ai-azure-openai-api-key"
