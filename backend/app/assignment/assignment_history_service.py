import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.config import settings


class AssignmentHistoryService:
    def __init__(self, store_path: Path | None = None) -> None:
        self.store_path = store_path or self._resolve_path(settings.assignment_history_store_path)

    def append_history_record(self, record: dict[str, Any]) -> dict[str, Any]:
        records = self._read_records()
        clean_record = {
            **record,
            "history_id": record.get("history_id") or f"ASSIGNHIST-{uuid4().hex[:12].upper()}",
            "timestamp": record.get("timestamp") or datetime.now(UTC).isoformat(),
            "comment": self._clean_comment(record.get("comment")),
        }
        records.append(clean_record)
        self._write_records(records)
        return clean_record

    def list_history_by_case(self, case_id: str) -> list[dict[str, Any]]:
        return self._newest_first([record for record in self._read_records() if record.get("case_id") == case_id])

    def list_history_by_user(self, user_id: str) -> list[dict[str, Any]]:
        return self._newest_first([
            record for record in self._read_records()
            if record.get("actor") == user_id or record.get("new_assigned_to") == user_id or record.get("previous_assigned_to") == user_id
        ])

    def list_all_history(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._newest_first(self._read_records())[:limit]

    def _read_records(self) -> list[dict[str, Any]]:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self._write_records([])
            return []
        data = json.loads(self.store_path.read_text(encoding="utf-8") or "[]")
        return data if isinstance(data, list) else []

    def _write_records(self, records: list[dict[str, Any]]) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.store_path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        temp_path.replace(self.store_path)

    @staticmethod
    def _newest_first(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(records, key=lambda item: str(item.get("timestamp") or ""), reverse=True)

    @staticmethod
    def _clean_comment(value: Any) -> str | None:
        if value is None:
            return None
        return str(value).replace("\n", " ").strip()[:500]

    @staticmethod
    def _resolve_path(path_value: str) -> Path:
        path = Path(path_value)
        if path.is_absolute():
            return path
        return Path(__file__).resolve().parents[3] / path
