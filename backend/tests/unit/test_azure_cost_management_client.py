from app.cost.azure_cost_management_client import AzureCostManagementClient


def test_azure_cost_management_client_returns_disabled_placeholder() -> None:
    result = AzureCostManagementClient().get_openai_resource_cost("2026-01-01", "2026-01-31")

    assert result["enabled"] is False
    assert "disabled" in result["message"].lower()
