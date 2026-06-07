import json
from pathlib import Path
from typing import Any

from app.alerting.json_file_store import resolve_store_path
from app.cost.cost_config import cost_monitoring_config
from app.observability.pii_safe_logging import sanitize_telemetry_properties


EMPTY_STORE = {"token_usage_records": [], "cost_records": []}


class CostRepository:
    def __init__(self, path_text: str | None = None) -> None:
        self.path = resolve_store_path(path_text or cost_monitoring_config.cost_local_store_path)

    def list_token_usage_records(self) -> list[dict]:
        return self._sorted(self._read()["token_usage_records"])

    def list_cost_records(self) -> list[dict]:
        return self._sorted(self._read()["cost_records"])

    def append_token_usage_record(self, record: dict) -> dict:
        data = self._read()
        data["token_usage_records"].append(self._sanitize_record(record))
        self._write(data)
        return record

    def append_cost_record(self, record: dict) -> dict:
        data = self._read()
        data["cost_records"].append(self._sanitize_record(record))
        self._write(data)
        return record

    def replace_cost_records(self, records: list[dict]) -> None:
        data = self._read()
        data["cost_records"] = [self._sanitize_record(record) for record in records]
        self._write(data)

    def list_by_case_id(self, case_id: str) -> dict:
        return self.search_records(case_id=case_id)

    def list_by_agent_name(self, agent_name: str) -> dict:
        return self.search_records(agent_name=agent_name)

    def list_by_model(self, model_or_deployment: str) -> dict:
        return self.search_records(model_or_deployment=model_or_deployment)

    def search_records(self, case_id: str | None = None, agent_name: str | None = None, model_or_deployment: str | None = None, start_date: str | None = None, end_date: str | None = None) -> dict:
        def match(record: dict) -> bool:
            return (
                (not case_id or record.get("case_id") == case_id)
                and (not agent_name or record.get("agent_name") == agent_name)
                and (not model_or_deployment or record.get("model_or_deployment") == model_or_deployment)
                and (not start_date or record.get("created_at", "") >= start_date)
                and (not end_date or record.get("created_at", "") <= end_date)
            )

        return {
            "token_usage_records": [record for record in self.list_token_usage_records() if match(record)],
            "cost_records": [record for record in self.list_cost_records() if match(record)],
        }

    def _read(self) -> dict[str, list[dict[str, Any]]]:
        if not self.path.exists():
            self._write(EMPTY_STORE)
            return {"token_usage_records": [], "cost_records": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8") or "{}")
        except json.JSONDecodeError:
            return {"token_usage_records": [], "cost_records": []}
        return {
            "token_usage_records": data.get("token_usage_records", []) if isinstance(data.get("token_usage_records", []), list) else [],
            "cost_records": data.get("cost_records", []) if isinstance(data.get("cost_records", []), list) else [],
        }

    def _write(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        temp.replace(self.path)

    @staticmethod
    def _sorted(records: list[dict]) -> list[dict]:
        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)

    @staticmethod
    def _sanitize_record(record: dict) -> dict:
        sanitized = dict(record)
        sanitized["metadata"] = sanitize_telemetry_properties(sanitized.get("metadata", {}))
        return sanitized
