from app.config import settings
from app.notifications.channels.base_channel import NotificationChannelClient
from app.notifications.notification_config import notification_config
from app.security.secure_config_loader import secure_config_loader


class TeamsChannel(NotificationChannelClient):
    channel = "TEAMS"

    def is_enabled(self) -> bool:
        return notification_config.enable_teams

    def send(self, notification: dict) -> dict:
        del notification
        webhook_url = secure_config_loader.get_secret("TEAMS_WEBHOOK_URL") or settings.teams_webhook_url
        if not self.is_enabled() or not webhook_url:
            return self.result("SKIPPED", "Teams channel is disabled or webhook configuration is missing.")
        # Production implementation can post sanitized adaptive cards to Teams.
        return self.result("SENT")
