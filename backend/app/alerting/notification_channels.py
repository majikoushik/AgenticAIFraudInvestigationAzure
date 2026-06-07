import json
from datetime import datetime
from uuid import uuid4

from app.alerting.json_file_store import JsonFileStore
from app.observability.pii_safe_logging import sanitize_telemetry_properties


class LocalNotificationChannel:
    def __init__(self, store: JsonFileStore | None = None) -> None:
        self.store = store or JsonFileStore("data/synthetic/notifications.json")

    def send(self, payload: dict) -> dict:
        notification = {
            "notification_id": f"NOTIF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
            "sent_at": datetime.utcnow().isoformat() + "Z",
            "status": "SENT",
            "error_message": None,
            **sanitize_telemetry_properties(payload),
        }
        records = self.store.read()
        records.append(notification)
        self.store.write(records[-1000:])
        return notification


class TeamsWebhookChannel:
    def send(self, payload: dict) -> dict:
        del payload
        return {"status": "SKIPPED", "error_message": "Teams webhook delivery is a production placeholder."}


class EmailNotificationChannel:
    def send(self, payload: dict) -> dict:
        del payload
        return {"status": "SKIPPED", "error_message": "SMTP delivery is a production placeholder."}
