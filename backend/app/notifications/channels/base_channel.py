from datetime import UTC, datetime


class NotificationChannelClient:
    channel = "BASE"

    def is_enabled(self) -> bool:
        return False

    def send(self, notification: dict) -> dict:
        del notification
        return self.result("SKIPPED", "Base channel is not sendable.")

    def result(self, status: str, error_message: str | None = None) -> dict:
        now = datetime.now(UTC).isoformat()
        return {
            "channel": self.channel,
            "status": status,
            "attempt_count": 1,
            "last_attempt_at": now,
            "error_message": error_message,
            "sent_at": now if status == "SENT" else None,
        }
