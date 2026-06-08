import json
from datetime import datetime
from uuid import uuid4

from app.alerting.json_file_store import resolve_store_path
from app.admin.admin_config import admin_config_settings
from app.admin.secret_masking import is_secret_key, mask_secret_value
from app.observability.correlation import get_correlation_id


class ConfigHistoryService:
    def __init__(self, path_text: str | None = None) -> None:
        self.path = resolve_store_path(path_text or admin_config_settings.history_store_path)

    def append_history_record(self, key: str, old_value, new_value, category: str, updated_by: str, comment: str | None = None) -> dict:
        now = datetime.utcnow().isoformat() + "Z"
        record = {
            "history_id": f"CONFHIST-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
            "key": key,
            "old_value": mask_secret_value(old_value) if is_secret_key(key) else old_value,
            "new_value": mask_secret_value(new_value) if is_secret_key(key) else new_value,
            "category": category,
            "updated_by": updated_by,
            "updated_at": now,
            "comment": comment,
            "correlation_id": get_correlation_id(),
        }
        records = self._read()
        records.append(record)
        self._write(records[-1000:])
        return record

    def list_history(self, key: str | None = None, category: str | None = None, limit: int = 100) -> list[dict]:
        records = sorted(self._read(), key=lambda item: item.get("updated_at", ""), reverse=True)
        if key:
            records = [record for record in records if record.get("key") == key]
        if category:
            records = [record for record in records if record.get("category") == category]
        return records[:limit]

    def _read(self) -> list[dict]:
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
        temp = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temp.write_text(json.dumps(records, indent=2, default=str), encoding="utf-8")
        temp.replace(self.path)
