from app.admin.admin_config import admin_config_settings


class KeyVaultConfigClient:
    def is_enabled(self) -> bool:
        return admin_config_settings.azure_key_vault_enabled

    def get_secret_status(self, secret_name: str) -> dict:
        if not self.is_enabled():
            return {"enabled": False, "message": "Key Vault integration is disabled."}
        return {"enabled": True, "secret_name": secret_name, "value_returned": False, "message": "TODO: check secret references with managed identity; never return secret values."}
