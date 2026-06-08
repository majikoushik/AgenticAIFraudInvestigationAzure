from app.admin.key_vault_config_client import KeyVaultConfigClient


def test_key_vault_config_client_disabled_placeholder() -> None:
    result = KeyVaultConfigClient().get_secret_status("AZURE_OPENAI_API_KEY")

    assert result["enabled"] is False
    assert "disabled" in result["message"].lower()
