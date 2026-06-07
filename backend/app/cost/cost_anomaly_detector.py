from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.cost.cost_config import cost_monitoring_config
from app.cost.cost_repository import CostRepository
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client


class CostAnomalyDetector:
    def __init__(self, repository: CostRepository | None = None) -> None:
        self.repository = repository or CostRepository()

    def detect_daily_cost_anomaly(self) -> dict:
        return self._detect("DAILY_COST_SPIKE", self._daily_values("estimated_total_cost", "cost_records"))

    def detect_token_usage_anomaly(self) -> dict:
        return self._detect("DAILY_TOKEN_USAGE_SPIKE", self._daily_values("total_tokens", "token_usage_records"))

    def detect_agent_cost_anomaly(self) -> dict:
        return self._detect_group("AGENT_COST_SPIKE", "agent_name")

    def detect_case_cost_anomaly(self) -> dict:
        return self._detect_group("CASE_COST_SPIKE", "case_id")

    def _detect(self, anomaly_type: str, values: dict[str, float]) -> dict:
        today = datetime.now(timezone.utc).date().isoformat()
        baseline_days = cost_monitoring_config.anomaly_min_baseline_days
        baseline_dates = [(datetime.now(timezone.utc).date() - timedelta(days=offset)).isoformat() for offset in range(1, baseline_days + 1)]
        baseline_values = [values.get(day, 0.0) for day in baseline_dates]
        if len([value for value in baseline_values if value > 0]) < baseline_days:
            return self._result(False, anomaly_type, values.get(today, 0.0), 0.0, 0.0, "NOT_ENOUGH_DATA")
        baseline = round(sum(baseline_values) / len(baseline_values), 6)
        current = values.get(today, 0.0)
        increase = round(((current - baseline) / baseline) * 100, 2) if baseline else 0.0
        detected = increase > cost_monitoring_config.anomaly_percent_increase_threshold
        result = self._result(detected, anomaly_type, current, baseline, increase, "ANOMALY" if detected else "NORMAL")
        if detected:
            self._emit(result)
        return result

    def _detect_group(self, anomaly_type: str, key: str) -> dict:
        grouped = defaultdict(float)
        for record in self.repository.list_cost_records():
            grouped[record.get(key) or "UNKNOWN"] += record.get("estimated_total_cost", 0)
        if not grouped:
            return self._result(False, anomaly_type, 0.0, 0.0, 0.0, "NOT_ENOUGH_DATA")
        name, current = max(grouped.items(), key=lambda item: item[1])
        threshold = cost_monitoring_config.cost_per_case_warning_threshold if key == "case_id" else 0
        detected = bool(threshold and current > threshold)
        result = self._result(detected, anomaly_type, current, threshold, 0.0, "ANOMALY" if detected else "NORMAL")
        result["group"] = name
        return result

    def _daily_values(self, field: str, store: str) -> dict[str, float]:
        records = self.repository.list_cost_records() if store == "cost_records" else self.repository.list_token_usage_records()
        grouped = defaultdict(float)
        for record in records:
            try:
                date_key = datetime.fromisoformat(record.get("created_at", "").replace("Z", "+00:00")).date().isoformat()
            except ValueError:
                continue
            grouped[date_key] += record.get(field, 0)
        return dict(grouped)

    @staticmethod
    def _result(detected: bool, anomaly_type: str, current: float, baseline: float, increase: float, status: str) -> dict:
        return {
            "anomaly_detected": detected,
            "anomaly_type": anomaly_type,
            "current_value": round(current, 6),
            "baseline_value": round(baseline, 6),
            "increase_percentage": increase,
            "threshold_percentage": cost_monitoring_config.anomaly_percent_increase_threshold,
            "status": status,
        }

    @staticmethod
    def _emit(result: dict) -> None:
        try:
            get_telemetry_client().track_event(telemetry_events.COST_ANOMALY_DETECTED, {"anomaly_type": result["anomaly_type"]}, {"current_value": result["current_value"], "baseline_value": result["baseline_value"]})
        except Exception:
            return None
