from datetime import datetime, timezone

from app.cost.cost_config import cost_monitoring_config
from app.cost.cost_repository import CostRepository
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client


class BudgetService:
    def __init__(self, repository: CostRepository | None = None) -> None:
        self.repository = repository or CostRepository()

    def get_budget_status(self) -> dict:
        daily = self.check_daily_budget()
        monthly = self.check_monthly_budget()
        tokens = self.check_token_daily_limit()
        statuses = {daily["status"], monthly["status"], tokens["status"]}
        status = "EXCEEDED" if "EXCEEDED" in statuses else "WARNING" if "WARNING" in statuses else "NOT_CONFIGURED" if statuses == {"NOT_CONFIGURED"} else "OK"
        result = {
            "daily_budget_limit": cost_monitoring_config.daily_budget_limit,
            "daily_estimated_cost": daily["daily_estimated_cost"],
            "daily_budget_used_percentage": daily["daily_budget_used_percentage"],
            "monthly_budget_limit": cost_monitoring_config.monthly_budget_limit,
            "monthly_estimated_cost": monthly["monthly_estimated_cost"],
            "monthly_budget_used_percentage": monthly["monthly_budget_used_percentage"],
            "token_daily_limit": cost_monitoring_config.token_daily_limit,
            "daily_tokens_used": tokens["daily_tokens_used"],
            "daily_token_limit_used_percentage": tokens["daily_token_limit_used_percentage"],
            "status": status,
            "case_thresholds": self.check_case_cost_thresholds(),
        }
        self._emit_if_needed(result)
        return result

    def check_daily_budget(self) -> dict:
        cost = self._cost_for_prefix(datetime.now(timezone.utc).date().isoformat())
        return self._budget_result("daily_estimated_cost", "daily_budget_used_percentage", cost, cost_monitoring_config.daily_budget_limit)

    def check_monthly_budget(self) -> dict:
        cost = self._cost_for_prefix(datetime.now(timezone.utc).strftime("%Y-%m"))
        return self._budget_result("monthly_estimated_cost", "monthly_budget_used_percentage", cost, cost_monitoring_config.monthly_budget_limit)

    def check_token_daily_limit(self) -> dict:
        today = datetime.now(timezone.utc).date().isoformat()
        tokens = sum(record.get("total_tokens", 0) for record in self.repository.list_token_usage_records() if record.get("created_at", "").startswith(today))
        percentage = round((tokens / cost_monitoring_config.token_daily_limit) * 100, 2) if cost_monitoring_config.token_daily_limit else 0.0
        return {"daily_tokens_used": tokens, "daily_token_limit_used_percentage": percentage, "status": self._status(percentage, cost_monitoring_config.token_daily_limit)}

    def check_case_cost_thresholds(self) -> dict:
        grouped = {}
        for record in self.repository.list_cost_records():
            case_id = record.get("case_id") or "UNKNOWN"
            grouped[case_id] = grouped.get(case_id, 0.0) + record.get("estimated_total_cost", 0.0)
        exceeded = [{"case_id": key, "estimated_cost": round(value, 6)} for key, value in grouped.items() if value > cost_monitoring_config.cost_per_case_warning_threshold]
        return {"threshold": cost_monitoring_config.cost_per_case_warning_threshold, "exceeded_cases": exceeded, "status": "WARNING" if exceeded else "OK"}

    def _cost_for_prefix(self, date_prefix: str) -> float:
        return round(sum(record.get("estimated_total_cost", 0) for record in self.repository.list_cost_records() if record.get("created_at", "").startswith(date_prefix)), 6)

    @staticmethod
    def _budget_result(cost_key: str, percentage_key: str, cost: float, limit: float) -> dict:
        percentage = round((cost / limit) * 100, 2) if limit else 0.0
        return {cost_key: cost, percentage_key: percentage, "status": BudgetService._status(percentage, limit)}

    @staticmethod
    def _status(percentage: float, limit: float | int) -> str:
        if not limit:
            return "NOT_CONFIGURED"
        if percentage >= 100:
            return "EXCEEDED"
        if percentage >= 80:
            return "WARNING"
        return "OK"

    @staticmethod
    def _emit_if_needed(result: dict) -> None:
        try:
            if result["status"] == "WARNING":
                get_telemetry_client().track_event(telemetry_events.BUDGET_WARNING, {"currency": cost_monitoring_config.currency}, {"daily_budget_used_percentage": result["daily_budget_used_percentage"]})
            if result["status"] == "EXCEEDED":
                get_telemetry_client().track_event(telemetry_events.BUDGET_EXCEEDED, {"currency": cost_monitoring_config.currency}, {"daily_budget_used_percentage": result["daily_budget_used_percentage"]})
        except Exception:
            return None
