from time import perf_counter

from app.core.constants import NotificationStatus
from app.notifications.channels.email_channel import EmailChannel
from app.notifications.channels.in_app_channel import InAppChannel
from app.notifications.channels.local_channel import LocalChannel
from app.notifications.channels.teams_channel import TeamsChannel
from app.notifications.channels.webhook_channel import WebhookChannel
from app.notifications.notification_preferences_service import NotificationPreferencesService
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client


class NotificationDispatcher:
    def __init__(self, preferences_service: NotificationPreferencesService | None = None) -> None:
        self.preferences_service = preferences_service or NotificationPreferencesService()
        self.channels = {
            "IN_APP": InAppChannel(),
            "LOCAL": LocalChannel(),
            "EMAIL": EmailChannel(),
            "TEAMS": TeamsChannel(),
            "WEBHOOK": WebhookChannel(),
        }

    def dispatch(self, notification: dict) -> dict:
        start = perf_counter()
        records = []
        channels = notification.get("channels") or []
        if notification.get("recipient_type") == "USER" and notification.get("recipient_id"):
            channels = self.preferences_service.get_effective_channels(notification["recipient_id"], notification["event_type"], channels)
        for channel in channels:
            records.append(self.dispatch_to_channel(notification, str(channel)))
        sent = [item for item in records if item["status"] == "SENT"]
        skipped = [item for item in records if item["status"] == "SKIPPED"]
        status = NotificationStatus.SENT.value if sent else NotificationStatus.SKIPPED.value if len(skipped) == len(records) else NotificationStatus.FAILED.value
        try:
            get_telemetry_client().track_event(
                telemetry_events.NOTIFICATION_DISPATCH_COMPLETED,
                {"event_type": notification.get("event_type"), "priority": notification.get("priority"), "status": status, "recipient_type": notification.get("recipient_type")},
                {"dispatch_duration_ms": round((perf_counter() - start) * 1000, 2), "channel_count": len(records)},
            )
        except Exception:
            pass
        return {"status": status, "delivery_records": records}

    def dispatch_to_channel(self, notification: dict, channel: str) -> dict:
        client = self.channels.get(channel)
        if not client:
            return {"channel": channel, "status": "SKIPPED", "attempt_count": 1, "last_attempt_at": None, "error_message": "Unknown channel.", "sent_at": None}
        try:
            result = client.send(notification)
            if result["status"] == "SKIPPED":
                get_telemetry_client().track_event(telemetry_events.NOTIFICATION_CHANNEL_SKIPPED, {"channel": channel, "event_type": notification.get("event_type")})
            return result
        except Exception as exc:
            return {"channel": channel, "status": "FAILED", "attempt_count": 1, "last_attempt_at": None, "error_message": type(exc).__name__, "sent_at": None}
