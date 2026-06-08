from pydantic import BaseModel

from app.config import settings


class NotificationConfig(BaseModel):
    enabled: bool = settings.notification_system_enabled
    mode: str = settings.notification_mode
    local_store_path: str = settings.notification_local_store_path
    preferences_store_path: str = settings.notification_preferences_store_path
    template_store_path: str = settings.notification_template_store_path
    enable_in_app: bool = settings.notification_enable_in_app
    enable_local: bool = settings.notification_enable_local
    enable_email: bool = settings.notification_enable_email
    enable_teams: bool = settings.notification_enable_teams
    enable_webhook: bool = settings.notification_enable_webhook
    default_channels: list[str] = [item.strip().upper() for item in settings.notification_default_channels.split(",") if item.strip()]
    max_retry_count: int = settings.notification_max_retry_count
    retry_delay_seconds: int = settings.notification_retry_delay_seconds
    retention_days: int = settings.notification_retention_days
    email_configured: bool = bool(settings.email_smtp_host and settings.email_from_address)
    teams_configured: bool = bool(settings.teams_webhook_url)
    webhook_configured: bool = bool(settings.generic_webhook_url)
    sanitize_payloads: bool = settings.notification_sanitize_payloads
    log_payloads: bool = settings.notification_log_payloads

    def safe_summary(self) -> dict:
        return {
            **self.model_dump(exclude={"local_store_path", "preferences_store_path", "template_store_path"}),
            "local_store_configured": bool(self.local_store_path),
            "preferences_store_configured": bool(self.preferences_store_path),
            "template_store_configured": bool(self.template_store_path),
            "secret_values_redacted": True,
        }


notification_config = NotificationConfig()
