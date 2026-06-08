from app.config import settings
from app.notifications.channels.base_channel import NotificationChannelClient
from app.notifications.notification_config import notification_config
from app.security.secure_config_loader import secure_config_loader


class WebhookChannel(NotificationChannelClient):
    channel = "WEBHOOK"

    def is_enabled(self) -> bool:
        return notification_config.enable_webhook

    def send(self, notification: dict) -> dict:
        del notification
        webhook_url = secure_config_loader.get_secret("TEAMS_WEBHOOK_URL") or settings.generic_webhook_url
        if not self.is_enabled() or not webhook_url:
            return self.result("SKIPPED", "Webhook channel is disabled or URL configuration is missing.")
        # Production implementation can send sanitized JSON with timeout and retry.
        return self.result("SENT")
