from app.admin.admin_config_schema import FEATURE_FLAG_KEYS
from app.admin.admin_config_service import AdminConfigService
from app.core.constants import AuditEventType, ReviewerRole
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.services.audit_service import audit_service
from app.services.errors import ApiError


class FeatureFlagService:
    def __init__(self, config_service: AdminConfigService | None = None) -> None:
        self.config_service = config_service or AdminConfigService()

    def list_feature_flags(self) -> list[dict]:
        return [self.get_feature_flag(flag) for flag in FEATURE_FLAG_KEYS]

    def get_feature_flag(self, flag_key: str) -> dict:
        if flag_key not in FEATURE_FLAG_KEYS:
            raise ApiError(404, "feature_flag_not_found", f"Feature flag {flag_key} was not found.")
        item = self.config_service.get_safe_config()["categories"]
        flags = next(category for category in item if category["category"] == "FEATURE_FLAGS")
        return next(flag for flag in flags["items"] if flag["key"] == flag_key)

    def update_feature_flag(self, flag_key: str, enabled: bool, updated_by: str, comment: str | None = None) -> dict:
        if flag_key not in FEATURE_FLAG_KEYS:
            raise ApiError(404, "feature_flag_not_found", f"Feature flag {flag_key} was not found.")
        response = self.config_service.update_config([{"key": flag_key, "value": enabled}], updated_by, comment)
        if response["failed_count"]:
            raise ApiError(400, "feature_flag_update_failed", "Feature flag update failed validation.")
        audit_service.record_event(None, AuditEventType.FEATURE_FLAG_UPDATED, updated_by, ReviewerRole.ADMIN, metadata={"flag_key": flag_key, "enabled": enabled})
        try:
            get_telemetry_client().track_event(telemetry_events.FEATURE_FLAG_UPDATED, {"flag_key": flag_key, "enabled": enabled})
        except Exception:
            pass
        return self.get_feature_flag(flag_key)

    def is_enabled(self, flag_key: str) -> bool:
        return bool(self.config_service.get_value(flag_key))
