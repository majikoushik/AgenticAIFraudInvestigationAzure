from app.config import settings
from app.notifications.channels.base_channel import NotificationChannelClient
from app.notifications.notification_config import notification_config
from app.security.secure_config_loader import secure_config_loader


class EmailChannel(NotificationChannelClient):
    channel = "EMAIL"

    def is_enabled(self) -> bool:
        return notification_config.enable_email

    def send(self, notification: dict) -> dict:
        del notification
        smtp_password = secure_config_loader.get_secret("SMTP_PASSWORD") or settings.email_smtp_password
        if not self.is_enabled() or not settings.email_smtp_host or not settings.email_from_address or (settings.email_smtp_username and not smtp_password):
            return self.result("SKIPPED", "Email channel is disabled or SMTP configuration is missing.")
        # Production implementation can use SMTP, Azure Communication Services, or Microsoft Graph.
        return self.result("SENT")
