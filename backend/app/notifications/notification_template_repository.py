import json
from pathlib import Path

from app.config import settings


class NotificationTemplateRepository:
    def __init__(self, store_path: Path | None = None) -> None:
        self.path = store_path or self._resolve(settings.notification_template_store_path)

    def list_templates(self) -> list[dict]:
        return self._read()

    def get_by_event_type(self, event_type: str) -> dict | None:
        return next((item for item in self._read() if item.get("event_type") == event_type and item.get("enabled", True)), None)

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
