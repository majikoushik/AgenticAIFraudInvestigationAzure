from app.admin.azure_app_config_client import AzureAppConfigClient


def test_azure_app_config_client_disabled_placeholder() -> None:
    result = AzureAppConfigClient().list_config()

    assert result["enabled"] is False
    assert "disabled" in result["message"].lower()
