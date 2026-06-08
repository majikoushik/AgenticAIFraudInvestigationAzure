import os
from dataclasses import dataclass, field


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() == "true"


@dataclass(frozen=True)
class AdminConfigSettings:
    enabled: bool = field(default_factory=lambda: _bool("ADMIN_CONFIG_ENABLED", True))
    mode: str = field(default_factory=lambda: os.getenv("ADMIN_CONFIG_MODE", "local"))
    local_store_path: str = field(default_factory=lambda: os.getenv("ADMIN_CONFIG_LOCAL_STORE_PATH", "data/synthetic/admin_config.json"))
    history_store_path: str = field(default_factory=lambda: os.getenv("ADMIN_CONFIG_HISTORY_STORE_PATH", "data/synthetic/admin_config_history.json"))
    allow_runtime_updates: bool = field(default_factory=lambda: _bool("ADMIN_CONFIG_ALLOW_RUNTIME_UPDATES", True))
    allow_reset_to_defaults: bool = field(default_factory=lambda: _bool("ADMIN_CONFIG_ALLOW_RESET_TO_DEFAULTS", True))
    require_admin_role: bool = field(default_factory=lambda: _bool("ADMIN_CONFIG_REQUIRE_ADMIN_ROLE", True))
    secret_keys_pattern: str = field(default_factory=lambda: os.getenv("CONFIG_SECRET_KEYS_PATTERN", "KEY,SECRET,TOKEN,PASSWORD,CONNECTION_STRING,WEBHOOK"))
    azure_app_configuration_enabled: bool = field(default_factory=lambda: _bool("AZURE_APP_CONFIGURATION_ENABLED", False))
    azure_app_configuration_endpoint: str = field(default_factory=lambda: os.getenv("AZURE_APP_CONFIGURATION_ENDPOINT", ""))
    azure_key_vault_enabled: bool = field(default_factory=lambda: _bool("AZURE_KEY_VAULT_ENABLED", False))
    azure_key_vault_uri: str = field(default_factory=lambda: os.getenv("AZURE_KEY_VAULT_URI", ""))

    def safe_summary(self) -> dict:
        return {
            "admin_config_enabled": self.enabled,
            "mode": self.mode,
            "allow_runtime_updates": self.allow_runtime_updates,
            "allow_reset_to_defaults": self.allow_reset_to_defaults,
            "require_admin_role": self.require_admin_role,
            "azure_app_configuration_enabled": self.azure_app_configuration_enabled,
            "azure_app_configuration_configured": bool(self.azure_app_configuration_endpoint),
            "key_vault_enabled": self.azure_key_vault_enabled,
            "key_vault_configured": bool(self.azure_key_vault_uri),
        }


admin_config_settings = AdminConfigSettings()
