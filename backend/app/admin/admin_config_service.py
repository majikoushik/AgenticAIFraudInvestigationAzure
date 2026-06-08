import os
from typing import Any

from app.admin.admin_config import admin_config_settings
from app.admin.admin_config_repository import AdminConfigRepository
from app.admin.admin_config_schema import SAFE_CONFIG_REGISTRY, ConfigDefinition
from app.admin.admin_config_validator import AdminConfigValidator
from app.admin.azure_app_config_client import AzureAppConfigClient
from app.admin.config_history_service import ConfigHistoryService
from app.admin.key_vault_config_client import KeyVaultConfigClient
from app.admin.secret_masking import sanitize_config_item
from app.core.constants import AuditEventType, ReviewerRole
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.services.audit_service import audit_service
from app.services.errors import ApiError
from app.notifications.integrations.safety_notifications import notify_safety_event
from app.security.security_health import security_health_service


class AdminConfigService:
    def __init__(self, repository: AdminConfigRepository | None = None, history_service: ConfigHistoryService | None = None) -> None:
        self.repository = repository or AdminConfigRepository()
        self.history_service = history_service or ConfigHistoryService()
        self.validator = AdminConfigValidator()

    def get_safe_config(self, actor: str = "system") -> dict:
        categories: dict[str, list[dict]] = {}
        for definition in SAFE_CONFIG_REGISTRY.values():
            if not definition.display:
                continue
            categories.setdefault(definition.category, []).append(self._build_item(definition))
        response = {"categories": [{"category": key, "items": sorted(items, key=lambda item: item["key"])} for key, items in sorted(categories.items())], "secret_values_redacted": True}
        audit_service.record_event(None, AuditEventType.ADMIN_CONFIG_VIEWED, actor, ReviewerRole.ADMIN, metadata={"category_count": len(categories)})
        self._track(telemetry_events.ADMIN_CONFIG_VIEWED, {"category_count": len(categories)})
        return response

    def get_config_by_category(self, category: str) -> dict:
        config = self.get_safe_config()
        found = next((item for item in config["categories"] if item["category"] == category), None)
        if not found:
            raise ApiError(404, "admin_config_category_not_found", f"Admin config category {category} was not found.")
        return found

    def update_config(self, updates: list[dict], updated_by: str, comment: str | None = None) -> dict:
        if not admin_config_settings.allow_runtime_updates:
            raise ApiError(403, "admin_config_updates_disabled", "Runtime admin configuration updates are disabled.")
        validation = self.validator.validate_batch_update(updates)
        errors = [result for result in validation if not result["valid"]]
        if errors:
            audit_service.record_event(None, AuditEventType.CONFIG_VALIDATION_FAILED, updated_by, ReviewerRole.ADMIN, metadata={"errors": errors})
            self._track(telemetry_events.CONFIG_VALIDATION_FAILED, {"failed_count": len(errors)})
            return {"updated_count": 0, "failed_count": len(errors), "updated_items": [], "validation_errors": errors, "message": "Configuration validation failed."}
        old_overrides = self.repository.get_overrides()
        update_map = {result["key"]: result["value"] for result in validation}
        self.repository.update_overrides(update_map)
        updated_items = []
        for key, new_value in update_map.items():
            definition = SAFE_CONFIG_REGISTRY[key]
            old_value = old_overrides.get(key, self._env_or_default(definition))
            self.history_service.append_history_record(key, old_value, new_value, definition.category, updated_by, comment)
            updated_items.append(self._build_item(definition))
            audit_service.record_event(None, AuditEventType.ADMIN_CONFIG_UPDATED, updated_by, ReviewerRole.ADMIN, metadata={"key": key, "old_value": old_value, "new_value": new_value, "category": definition.category, "requires_restart": definition.requires_restart})
            notify_safety_event("FEATURE_FLAG_UPDATED" if key.startswith("FEATURE_") else "ADMIN_CONFIG_UPDATED", {"key": key, "category": definition.category, "updated_by": updated_by, "priority": "INFO"})
        self._track(telemetry_events.ADMIN_CONFIG_UPDATED, {"updated_count": len(updated_items)})
        return {"updated_count": len(updated_items), "failed_count": 0, "updated_items": updated_items, "validation_errors": [], "message": "Configuration updated successfully."}

    def reset_to_defaults(self, updated_by: str, comment: str | None = None) -> dict:
        if not admin_config_settings.allow_reset_to_defaults:
            raise ApiError(403, "admin_config_reset_disabled", "Reset to defaults is disabled.")
        old = self.repository.get_overrides()
        self.repository.reset_overrides()
        for key, value in old.items():
            definition = SAFE_CONFIG_REGISTRY.get(key)
            if definition:
                self.history_service.append_history_record(key, value, self._env_or_default(definition), definition.category, updated_by, comment or "Reset local overrides to defaults.")
        audit_service.record_event(None, AuditEventType.ADMIN_CONFIG_RESET, updated_by, ReviewerRole.ADMIN, metadata={"reset_count": len(old)})
        self._track(telemetry_events.ADMIN_CONFIG_RESET, {"reset_count": len(old)})
        return {"reset_count": len(old), "message": "Local non-secret overrides reset to defaults."}

    def get_config_history(self, key: str | None = None, category: str | None = None, limit: int = 100) -> list[dict]:
        return self.history_service.list_history(key, category, limit)

    def get_config_health(self) -> dict:
        editable = [definition for definition in SAFE_CONFIG_REGISTRY.values() if definition.editable and not definition.secret]
        restart = [definition for definition in SAFE_CONFIG_REGISTRY.values() if definition.requires_restart]
        security_health = security_health_service.get_security_health()
        return {
            **admin_config_settings.safe_summary(),
            "local_store_accessible": self._path_accessible(self.repository.path),
            "history_store_accessible": self._path_accessible(self.history_service.path),
            "azure_app_configuration_enabled": AzureAppConfigClient().is_enabled(),
            "key_vault_enabled": KeyVaultConfigClient().is_enabled(),
            "deployment_security": {
                "deployment_mode": security_health["deployment_mode"],
                "secret_provider": security_health["secret_provider"],
                "key_vault_configured": security_health["key_vault_configured"],
                "managed_identity_enabled": security_health["managed_identity_enabled"],
                "managed_identity_configured": security_health["managed_identity_configured"],
                "private_endpoints_enabled": security_health["private_endpoints_enabled"],
                "public_network_access_disabled": security_health["public_network_access_disabled"],
                "status": security_health["status"],
                "warnings": security_health["warnings"],
            },
            "secret_values_redacted": True,
            "editable_config_count": len(editable),
            "requires_restart_count": len(restart),
        }

    def get_value(self, key: str) -> Any:
        definition = SAFE_CONFIG_REGISTRY[key]
        override = self.repository.get_override(key)
        return override if override is not None else self._env_or_default(definition)

    def _build_item(self, definition: ConfigDefinition) -> dict:
        overrides = self.repository.get_overrides()
        value = overrides.get(definition.key, self._env_or_default(definition))
        source = "local_store" if definition.key in overrides else "environment" if os.getenv(definition.key) is not None else "default"
        item = {
            "key": definition.key,
            "value": value,
            "default_value": definition.default_value,
            "category": definition.category,
            "data_type": definition.data_type,
            "editable": definition.editable,
            "secret": definition.secret,
            "description": definition.description,
            "allowed_values": definition.allowed_values,
            "min_value": definition.min_value,
            "max_value": definition.max_value,
            "requires_restart": definition.requires_restart,
            "source": source,
            "last_updated_at": None,
            "last_updated_by": None,
        }
        latest = next((record for record in self.history_service.list_history(key=definition.key, limit=1)), None)
        if latest:
            item["last_updated_at"] = latest.get("updated_at")
            item["last_updated_by"] = latest.get("updated_by")
        return sanitize_config_item(item)

    @staticmethod
    def _env_or_default(definition: ConfigDefinition):
        raw = os.getenv(definition.key)
        if raw is None:
            return definition.default_value
        return AdminConfigValidator._coerce(raw, definition.data_type, [])

    @staticmethod
    def _path_accessible(path) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("[]" if "history" in path.name else '{"overrides": {}}', encoding="utf-8")
            return True
        except OSError:
            return False

    @staticmethod
    def _track(event_name: str, properties: dict) -> None:
        try:
            get_telemetry_client().track_event(event_name, properties)
        except Exception:
            return None
