from app.notifications.channels.base_channel import NotificationChannelClient
from app.notifications.notification_config import notification_config


class InAppChannel(NotificationChannelClient):
    channel = "IN_APP"

    def is_enabled(self) -> bool:
        return notification_config.enable_in_app

    def send(self, notification: dict) -> dict:
        del notification
        return self.result("SENT" if self.is_enabled() else "SKIPPED", None if self.is_enabled() else "In-app channel disabled.")
