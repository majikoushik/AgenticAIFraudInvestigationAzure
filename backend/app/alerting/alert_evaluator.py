import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.alerting.alert_config import alerting_config
from app.alerting.alert_rules import alert_rules
from app.core.constants import AlertType, CaseStatus
from app.repositories.case_repository import CaseRepository
from app.services.metrics_service import MetricsService
from app.cost.budget_service import BudgetService
from app.cost.cost_anomaly_detector import CostAnomalyDetector
from app.cost.cost_config import cost_monitoring_config
from app.cost.cost_service import CostService


class AlertEvaluator:
    def __init__(self, metrics_service: MetricsService | None = None, case_repository: CaseRepository | None = None) -> None:
        self.metrics_service = metrics_service or MetricsService()
        self.case_repository = case_repository or CaseRepository()
        self.cost_service = CostService()
        self.budget_service = BudgetService(self.cost_service.repository)
        self.cost_anomaly_detector = CostAnomalyDetector(self.cost_service.repository)

    def evaluate_all_rules(self) -> list[dict]:
        results = []
        metrics = self.metrics_service.get_summary_metrics()
        telemetry = self._telemetry_events()
        for rule in alert_rules():
            alert = self._evaluate_rule(rule, metrics, telemetry)
            status = "TRIGGERED" if alert else self._non_triggered_status(rule, telemetry)
            reason = None if alert else ("Telemetry source missing or no relevant events." if status == "NOT_ENOUGH_DATA" else "Threshold not met.")
            results.append({"alert_type": rule["alert_type"], "status": status, "alert": alert, "reason": reason})
        return results

    def _evaluate_rule(self, rule: dict, metrics, telemetry: list[dict]) -> dict | None:
        alert_type = rule["alert_type"]
        metric_value = None
        if alert_type == AlertType.HIGH_API_ERROR_RATE.value:
            completed = [event for event in telemetry if event.get("name") == "API_REQUEST_COMPLETED"]
            error_count = sum(1 for event in completed if self._status_code(event) >= 500)
            metric_value = (error_count / len(completed) * 100) if completed else 0
            triggered = bool(completed) and metric_value > rule["threshold_value"]
        elif alert_type == AlertType.HIGH_API_LATENCY.value:
            values = self._measurement_values(telemetry, "API_REQUEST_COMPLETED", "duration_ms")
            metric_value = sum(values) / len(values) if values else 0
            triggered = bool(values) and metric_value > rule["threshold_value"]
        elif alert_type == AlertType.HIGH_AGENT_FAILURE_RATE.value:
            metric_value = metrics.agent_execution_metrics.agent_failure_count
            triggered = metric_value > rule["threshold_value"]
        elif alert_type == AlertType.HIGH_RAG_EMPTY_RESULT_RATE.value:
            metric_value = self._count_events(telemetry, "RAG_EMPTY_RESULT")
            triggered = metric_value > rule["threshold_value"]
        elif alert_type == AlertType.CITATION_VALIDATION_FAILURE.value:
            metric_value = self._count_events(telemetry, "CITATION_VALIDATION_FAILED")
            triggered = metric_value >= 1
        elif alert_type == AlertType.HIGH_LLM_LATENCY.value:
            values = self._measurement_values(telemetry, "LLM_CALL_COMPLETED", "latency_ms")
            metric_value = sum(values) / len(values) if values else 0
            triggered = bool(values) and metric_value > rule["threshold_value"]
        elif alert_type == AlertType.HIGH_TOKEN_USAGE.value:
            metric_value = sum(self._measurement_values(telemetry, "LLM_TOKEN_USAGE_RECORDED", "total_tokens"))
            triggered = metric_value > rule["threshold_value"]
        elif alert_type == AlertType.HIGH_COST_ESTIMATE.value:
            metric_value = self.budget_service.check_daily_budget()["daily_estimated_cost"]
            triggered = cost_monitoring_config.daily_budget_limit > 0 and metric_value > cost_monitoring_config.daily_budget_limit
        elif alert_type == AlertType.BUDGET_WARNING.value:
            status = self.budget_service.get_budget_status()["status"]
            metric_value = self.budget_service.get_budget_status()["daily_budget_used_percentage"]
            triggered = status == "WARNING"
        elif alert_type == AlertType.BUDGET_EXCEEDED.value:
            status = self.budget_service.get_budget_status()["status"]
            metric_value = self.budget_service.get_budget_status()["daily_budget_used_percentage"]
            triggered = status == "EXCEEDED"
        elif alert_type == AlertType.COST_ANOMALY_DETECTED.value:
            anomaly = self.cost_anomaly_detector.detect_daily_cost_anomaly()
            metric_value = anomaly.get("increase_percentage", 0)
            triggered = anomaly.get("status") == "ANOMALY"
        elif alert_type == AlertType.HIGH_CASE_COST_DETECTED.value:
            thresholds = self.budget_service.check_case_cost_thresholds()
            metric_value = len(thresholds.get("exceeded_cases", []))
            triggered = metric_value > 0
        elif alert_type == AlertType.HIGH_AGENT_COST_DETECTED.value:
            agents = self.cost_service.get_agent_cost_breakdown()["agents"]
            metric_value = max((agent.get("estimated_cost", 0) for agent in agents), default=0)
            triggered = cost_monitoring_config.daily_budget_limit > 0 and metric_value > cost_monitoring_config.daily_budget_limit
        elif alert_type == AlertType.PROMPT_INJECTION_DETECTED.value:
            metric_value = self._count_events(telemetry, "PROMPT_INJECTION_DETECTED")
            triggered = metric_value >= 1
        elif alert_type == AlertType.GUARDRAIL_VIOLATION_DETECTED.value:
            metric_value = self._count_events(telemetry, "GUARDRAIL_VIOLATION_DETECTED")
            triggered = metric_value >= 1
        elif alert_type == AlertType.HIGH_HUMAN_OVERRIDE_RATE.value:
            metric_value = metrics.human_override_metrics.override_rate_percentage
            triggered = metric_value > rule["threshold_value"]
        elif alert_type == AlertType.CASES_STUCK_PENDING_REVIEW.value:
            metric_value = self._stuck_pending_review_count()
            triggered = metric_value >= 1
        elif alert_type == AlertType.POLICY_CITATION_ACCURACY_LOW.value:
            metric_value = metrics.policy_citation_metrics.policy_reference_rate_percentage
            triggered = metrics.case_status_metrics.total_cases > 0 and metric_value < rule["threshold_value"]
        else:
            triggered = False
        if not triggered:
            return None
        return {**rule, "metric_value": float(metric_value or 0), "source": "local_evaluator", "properties": {"evaluation": "local"}}

    @staticmethod
    def _telemetry_events() -> list[dict]:
        from app.config import get_synthetic_data_path
        path = get_synthetic_data_path() / "telemetry_events.json"
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8") or "[]")
        except json.JSONDecodeError:
            return []

    @staticmethod
    def _count_events(events: list[dict], name: str) -> int:
        return sum(1 for event in events if event.get("name") == name)

    @staticmethod
    def _measurement_values(events: list[dict], name: str, key: str) -> list[float]:
        return [float((event.get("measurements") or {}).get(key, 0)) for event in events if event.get("name") == name and (event.get("measurements") or {}).get(key) is not None]

    @staticmethod
    def _status_code(event: dict) -> int:
        try:
            return int((event.get("properties") or {}).get("status_code", 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _non_triggered_status(rule: dict, telemetry: list[dict]) -> str:
        telemetry_rules = {
            AlertType.HIGH_API_ERROR_RATE.value,
            AlertType.HIGH_API_LATENCY.value,
            AlertType.HIGH_RAG_EMPTY_RESULT_RATE.value,
            AlertType.CITATION_VALIDATION_FAILURE.value,
            AlertType.HIGH_LLM_LATENCY.value,
            AlertType.HIGH_TOKEN_USAGE.value,
            AlertType.PROMPT_INJECTION_DETECTED.value,
            AlertType.GUARDRAIL_VIOLATION_DETECTED.value,
        }
        return "NOT_ENOUGH_DATA" if rule["alert_type"] in telemetry_rules and not telemetry else "OK"

    def _stuck_pending_review_count(self) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=alerting_config.stuck_pending_review_hours)
        count = 0
        for case in self.case_repository.list_alerts():
            if case.get("status") != CaseStatus.PENDING_HUMAN_REVIEW.value:
                continue
            timestamp_text = case.get("status_updated_at") or case.get("created_at")
            try:
                timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
                if timestamp < cutoff:
                    count += 1
            except Exception:
                continue
        return count
