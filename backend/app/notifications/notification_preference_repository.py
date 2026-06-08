import json
from datetime import UTC, datetime
from pathlib import Path

from app.config import settings


class NotificationPreferenceRepository:
    def __init__(self, store_path: Path | None = None) -> None:
        self.path = store_path or self._resolve(settings.notification_preferences_store_path)

    def list_preferences(self) -> list[dict]:
        return self._read()

    def get_by_user_id(self, user_id: str) -> dict | None:
        return next((item for item in self._read() if item.get("user_id") == user_id), None)

    def upsert(self, user_id: str, preference: dict) -> dict:
        records = self._read()
        updated = {**preference, "user_id": user_id, "updated_at": datetime.now(UTC).isoformat()}
        for index, item in enumerate(records):
            if item.get("user_id") == user_id:
                records[index] = updated
                self._write(records)
                return updated
        records.append(updated)
        self._write(records)
        return updated

    def _read(self) -> list[dict]:
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
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(records, indent=2), encoding="utf-8")
        temp.replace(self.path)

    @staticmethod
    def _resolve(path_value: str) -> Path:
        path = Path(path_value)
        return path if path.is_absolute() else Path(__file__).resolve().parents[3] / path
