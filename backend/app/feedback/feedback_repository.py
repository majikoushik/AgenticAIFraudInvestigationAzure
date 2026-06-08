import json
from pathlib import Path
from typing import Any

from app.config import settings
from app.feedback.feedback_sanitizer import sanitize_feedback_payload


class FeedbackRepository:
    def __init__(self, store_path: Path | None = None) -> None:
        self.path = store_path or self._resolve(settings.feedback_local_store_path)

    def list_feedback(self) -> list[dict[str, Any]]:
        return self._newest_first(self._read().get("feedback_records", []))

    def get_feedback_by_id(self, feedback_id: str) -> dict[str, Any] | None:
        return next((item for item in self._read().get("feedback_records", []) if item.get("feedback_id") == feedback_id), None)

    def append_feedback(self, feedback: dict[str, Any]) -> dict[str, Any]:
        data = self._read()
        records = data.get("feedback_records", [])
        clean = sanitize_feedback_payload(feedback)
        records.append(clean)
        data["feedback_records"] = records[-10000:]
        self._write(data)
        return clean

    def update_feedback(self, feedback_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        data = self._read()
        records = data.get("feedback_records", [])
        for item in records:
            if item.get("feedback_id") == feedback_id:
                item.update(sanitize_feedback_payload(updates))
                self._write(data)
                return item
        raise KeyError(feedback_id)

    def search_feedback(
        self,
        case_id: str | None = None,
        target_type: str | None = None,
        rating: str | None = None,
        issue_type: str | None = None,
        severity: str | None = None,
        disposition: str | None = None,
        submitted_by: str | None = None,
        agent_name: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        result = self.list_feedback()
        filters = {
            "case_id": case_id,
            "target_type": target_type,
            "rating": rating,
            "severity": severity,
            "disposition": disposition,
            "submitted_by": submitted_by,
            "agent_name": agent_name,
        }
        for key, value in filters.items():
            if value:
                result = [item for item in result if str(item.get(key)) == str(value)]
        if issue_type:
            result = [item for item in result if issue_type in item.get("issue_types", [])]
        if start_date:
            result = [item for item in result if str(item.get("created_at", "")) >= start_date]
        if end_date:
            result = [item for item in result if str(item.get("created_at", "")) <= end_date]
        return result[:limit]

    def _read(self) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"feedback_records": []})
            return {"feedback_records": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8") or "{}")
            if isinstance(data, dict) and isinstance(data.get("feedback_records"), list):
                return data
        except json.JSONDecodeError:
            pass
        return {"feedback_records": []}

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temp_path.replace(self.path)

    @staticmethod
    def _newest_first(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(records, key=lambda item: str(item.get("created_at") or ""), reverse=True)

    @staticmethod
    def _resolve(path_value: str) -> Path:
        path = Path(path_value)
        return path if path.is_absolute() else Path(__file__).resolve().parents[3] / path
