import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.compliance.retention_config import retention_config
from app.core.constants import DataCategory
from app.services.errors import ApiError


SOURCE_MAP: dict[DataCategory, tuple[str, str | None, list[str]]] = {
    DataCategory.FRAUD_CASE: ("data/synthetic/fraud_alerts.json", None, ["case_id", "alert_id", "id"]),
    DataCategory.AUDIT_EVENT: ("data/synthetic/audit_events.json", None, ["audit_id", "id"]),
    DataCategory.FEEDBACK_RECORD: ("data/synthetic/ai_feedback.json", "feedback_records", ["feedback_id", "id"]),
    DataCategory.NOTIFICATION_RECORD: ("data/synthetic/notifications.json", None, ["notification_id", "id"]),
    DataCategory.INCIDENT_RECORD: ("data/synthetic/incidents.json", None, ["incident_id", "id"]),
    DataCategory.ALERT_RECORD: ("data/synthetic/alerts.json", None, ["alert_id", "id"]),
    DataCategory.COST_RECORD: ("data/synthetic/cost_records.json", None, ["cost_id", "usage_id", "id"]),
    DataCategory.ASSIGNMENT_HISTORY: ("data/synthetic/assignment_history.json", None, ["assignment_id", "history_id", "case_id", "id"]),
    DataCategory.CONFIG_HISTORY: ("data/synthetic/admin_config_history.json", None, ["history_id", "id"]),
    DataCategory.TELEMETRY_RECORD: ("data/synthetic/telemetry_events.json", None, ["event_id", "id"]),
}

CREATED_AT_KEYS = ["created_at", "timestamp", "event_timestamp", "requested_at", "sent_at", "assigned_at", "updated_at"]


class RetentionRepository:
    def list_records_by_category(self, data_category: str) -> list[dict]:
        category = DataCategory(data_category)
        source = SOURCE_MAP.get(category)
        if not source:
            return []
        payload = self._read_source(category)
        records = self._records_from_payload(payload, source[1])
        return [record for record in records if isinstance(record, dict)]

    def get_record_created_at(self, record: dict, data_category: str) -> datetime | None:
        metadata = record.get("retention_metadata") or {}
        raw = metadata.get("created_at")
        if raw:
            return self._parse_datetime(raw)
        for key in CREATED_AT_KEYS:
            if record.get(key):
                return self._parse_datetime(record[key])
        return None

    def get_record_id(self, record: dict, data_category: str) -> str:
        category = DataCategory(data_category)
        for key in SOURCE_MAP.get(category, ("", None, ["id"]))[2]:
            if record.get(key):
                return str(record[key])
        return f"{category.value}-{abs(hash(json.dumps(record, sort_keys=True, default=str)))}"

    def get_case_id(self, record: dict) -> str | None:
        return record.get("case_id") or record.get("alert_id") or record.get("related_case_id")

    def update_record_retention_metadata(self, data_category: str, record_id: str, metadata: dict) -> dict:
        category = DataCategory(data_category)
        payload = self._read_source(category)
        root_key = SOURCE_MAP[category][1]
        records = self._records_from_payload(payload, root_key)
        for record in records:
            if self.get_record_id(record, category.value) == record_id:
                record["retention_metadata"] = metadata
                self._write_source(category, payload)
                return record
        raise ApiError(404, "retention_record_not_found", f"Record {record_id} was not found.")

    def archive_record(self, data_category: str, record_id: str, archive_path: str) -> dict:
        category = DataCategory(data_category)
        record = self._find_record(category, record_id)
        target = Path(archive_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
        metadata = record.get("retention_metadata") or {}
        metadata.update({"retention_status": "ARCHIVED", "archived_at": datetime.now(UTC).isoformat(), "archive_path": str(target)})
        self.update_record_retention_metadata(category.value, record_id, metadata)
        return {"record_id": record_id, "data_category": category.value, "archive_path": str(target), "status": "ARCHIVED"}

    def purge_record(self, data_category: str, record_id: str, dry_run: bool = True) -> dict:
        category = DataCategory(data_category)
        if dry_run:
            self._find_record(category, record_id)
            return {"record_id": record_id, "data_category": category.value, "dry_run": True, "would_purge": True}
        payload = self._read_source(category)
        root_key = SOURCE_MAP[category][1]
        records = self._records_from_payload(payload, root_key)
        remaining = [record for record in records if self.get_record_id(record, category.value) != record_id]
        if len(remaining) == len(records):
            raise ApiError(404, "retention_record_not_found", f"Record {record_id} was not found.")
        if root_key:
            payload[root_key] = remaining
        else:
            payload = remaining
        self._write_source(category, payload)
        return {"record_id": record_id, "data_category": category.value, "dry_run": False, "purged": True}

    def source_file_for_category(self, data_category: str) -> str:
        category = DataCategory(data_category)
        return SOURCE_MAP.get(category, ("", None, []))[0]

    def _find_record(self, category: DataCategory, record_id: str) -> dict:
        for record in self.list_records_by_category(category.value):
            if self.get_record_id(record, category.value) == record_id:
                return record
        raise ApiError(404, "retention_record_not_found", f"Record {record_id} was not found.")

    def _read_source(self, category: DataCategory):
        path = retention_config.resolve_path(SOURCE_MAP[category][0])
        if not path.exists():
            return {SOURCE_MAP[category][1]: []} if SOURCE_MAP[category][1] else []
        return json.loads(path.read_text(encoding="utf-8") or "[]")

    def _write_source(self, category: DataCategory, payload) -> None:
        path = retention_config.resolve_path(SOURCE_MAP[category][0])
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
        shutil.move(str(temp), str(path))

    @staticmethod
    def _records_from_payload(payload: Any, root_key: str | None) -> list:
        if root_key:
            return payload.get(root_key, []) if isinstance(payload, dict) else []
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for value in payload.values():
                if isinstance(value, list):
                    return value
        return []

    @staticmethod
    def _parse_datetime(value: str) -> datetime | None:
        try:
            text = str(value).replace("Z", "+00:00")
            parsed = datetime.fromisoformat(text)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except (TypeError, ValueError):
            return None


retention_repository = RetentionRepository()
