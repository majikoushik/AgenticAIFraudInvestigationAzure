from typing import Any

from app.admin.admin_config import admin_config_settings


class AzureAppConfigClient:
    def is_enabled(self) -> bool:
        return admin_config_settings.azure_app_configuration_enabled

    def get_config(self, key: str) -> dict:
        if not self.is_enabled():
            return self._disabled()
        return {"enabled": True, "key": key, "message": "TODO: integrate Azure App Configuration with managed identity."}

    def set_config(self, key: str, value: Any) -> dict:
        if not self.is_enabled():
            return self._disabled()
        return {"enabled": True, "key": key, "updated": False, "message": "TODO: write non-secret config through Azure App Configuration."}

    def list_config(self) -> dict:
        if not self.is_enabled():
            return self._disabled()
        return {"enabled": True, "items": [], "message": "TODO: list Azure App Configuration keys."}

    @staticmethod
    def _disabled() -> dict:
        return {"enabled": False, "message": "Azure App Configuration integration is disabled. Using local admin config overrides."}
