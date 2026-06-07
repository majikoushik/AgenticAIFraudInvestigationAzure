from app.cost.cost_config import cost_monitoring_config


class AzureCostManagementClient:
    def is_enabled(self) -> bool:
        return cost_monitoring_config.azure_cost_management_enabled

    def get_openai_resource_cost(self, start_date: str, end_date: str) -> dict:
        return self._disabled_or_placeholder("azure_openai", start_date, end_date)

    def get_search_resource_cost(self, start_date: str, end_date: str) -> dict:
        return self._disabled_or_placeholder("azure_ai_search", start_date, end_date)

    def get_total_resource_group_cost(self, start_date: str, end_date: str) -> dict:
        return self._disabled_or_placeholder("resource_group", start_date, end_date)

    def _disabled_or_placeholder(self, scope: str, start_date: str, end_date: str) -> dict:
        if not self.is_enabled():
            return {"enabled": False, "message": "Azure Cost Management integration is disabled. Using local estimated cost records."}
        return {
            "enabled": True,
            "scope": scope,
            "start_date": start_date,
            "end_date": end_date,
            "message": "TODO: integrate Azure Cost Management using managed identity in production.",
        }
