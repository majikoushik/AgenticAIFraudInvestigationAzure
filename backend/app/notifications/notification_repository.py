import json
from pathlib import Path
from typing import Any

from app.config import settings
from app.notifications.notification_sanitizer import sanitize_notification_payload


class NotificationRepository:
    def __init__(self, store_path: Path | None = None) -> None:
        self.path = store_path or self._resolve(settings.notification_local_store_path)

    def list_notifications(self) -> list[dict]:
        return self._newest_first(self._read())

    def get_notification_by_id(self, notification_id: str) -> dict | None:
        return next((item for item in self._read() if item.get("notification_id") == notification_id), None)

    def append_notification(self, notification: dict) -> dict:
        records = self._read()
        clean = sanitize_notification_payload(notification)
        records.append(clean)
        self._write(records[-5000:])
        return clean

    def update_notification(self, notification_id: str, updates: dict) -> dict:
        records = self._read()
        for item in records:
            if item.get("notification_id") == notification_id:
                item.update(sanitize_notification_payload(updates))
                self._write(records)
                return item
        raise KeyError(notification_id)

    def search_notifications(
        self,
        recipient_id: str | None = None,
        recipient_role: str | None = None,
        recipient_team: str | None = None,
        event_type: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        read: bool | None = None,
        archived: bool | None = None,
        case_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        result = self.list_notifications()
        if recipient_id:
            result = [item for item in result if item.get("recipient_id") == recipient_id]
        if recipient_role:
            result = [item for item in result if item.get("recipient_role") == recipient_role]
        if recipient_team:
            result = [item for item in result if item.get("recipient_team") == recipient_team]
        for key, value in {"event_type": event_type, "priority": priority, "status": status, "case_id": case_id}.items():
            if value:
                result = [item for item in result if str(item.get(key)) == str(value)]
        if read is not None:
            result = [item for item in result if bool(item.get("read")) is read]
        if archived is not None:
            result = [item for item in result if bool(item.get("archived")) is archived]
        if start_date:
            result = [item for item in result if str(item.get("created_at", "")) >= start_date]
        if end_date:
            result = [item for item in result if str(item.get("created_at", "")) <= end_date]
        return result[:limit]

    def _read(self) -> list[dict[str, Any]]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8") or "[]")
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    def _write(self, records: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        temp_path.replace(self.path)

    @staticmethod
    def _newest_first(records: list[dict]) -> list[dict]:
        return sorted(records, key=lambda item: str(item.get("created_at") or ""), reverse=True)

    @staticmethod
    def _resolve(path_value: str) -> Path:
        path = Path(path_value)
        return path if path.is_absolute() else Path(__file__).resolve().parents[3] / path
