from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from app.cost.cost_config import CostMonitoringConfig, cost_monitoring_config
from app.cost.cost_estimator import CostEstimator
from app.cost.cost_repository import CostRepository
from app.repositories.case_repository import CaseRepository


class CostService:
    def __init__(self, repository: CostRepository | None = None, case_repository: CaseRepository | None = None) -> None:
        self.repository = repository or CostRepository()
        self.case_repository = case_repository or CaseRepository()

    def get_cost_summary(self) -> dict:
        costs = self.repository.list_cost_records()
        usage = self.repository.list_token_usage_records()
        case_totals = self._group_costs("case_id", costs)
        agent_totals = self._group_costs("agent_name", costs)
        return {
            "total_prompt_tokens": sum(record.get("prompt_tokens", 0) for record in usage),
            "total_completion_tokens": sum(record.get("completion_tokens", 0) for record in usage),
            "total_tokens": sum(record.get("total_tokens", 0) for record in usage),
            "estimated_total_cost": round(sum(record.get("estimated_total_cost", 0) for record in costs), 6),
            "currency": cost_monitoring_config.currency,
            "total_cases_with_cost": len([case for case in case_totals if case]),
            "average_cost_per_case": self._average([item["estimated_cost"] for item in case_totals.values()]),
            "average_tokens_per_case": self._average([item["total_tokens"] for item in case_totals.values()]),
            "highest_cost_case_id": self._highest_key(case_totals, "estimated_cost"),
            "highest_cost_agent": self._highest_key(agent_totals, "estimated_cost"),
            "pricing_configured": any((record.get("metadata") or {}).get("pricing_configured") for record in costs),
        }

    def get_token_usage_summary(self, filters: dict | None = None) -> dict:
        records = self.repository.search_records(**(filters or {}))["token_usage_records"]
        return {
            "count": len(records),
            "total_prompt_tokens": sum(record.get("prompt_tokens", 0) for record in records),
            "total_completion_tokens": sum(record.get("completion_tokens", 0) for record in records),
            "total_tokens": sum(record.get("total_tokens", 0) for record in records),
            "by_provider": self._token_counter(records, "ai_provider"),
            "by_model": self._token_counter(records, "model_or_deployment"),
            "records": records,
        }

    def get_case_cost_breakdown(self, case_id: str) -> dict:
        records = self.repository.list_by_case_id(case_id)
        costs = records["cost_records"]
        usage = records["token_usage_records"]
        case = next((item for item in self.case_repository.list_alerts() if item.get("case_id") == case_id), {})
        return {
            "case_id": case_id,
            "case_status": case.get("status"),
            "ai_recommendation": case.get("ai_recommendation"),
            "human_decision": (case.get("human_review") or {}).get("human_decision") if isinstance(case.get("human_review"), dict) else None,
            "human_override": bool((case.get("override_summary") or {}).get("has_override")) if isinstance(case.get("override_summary"), dict) else False,
            "total_tokens": sum(record.get("total_tokens", 0) for record in usage),
            "estimated_total_cost": round(sum(record.get("estimated_total_cost", 0) for record in costs), 6),
            "currency": cost_monitoring_config.currency,
            "agent_breakdown": list(self._group_costs("agent_name", costs).values()),
            "token_usage_records": usage,
            "cost_records": costs,
        }

    def get_agent_cost_breakdown(self) -> dict:
        return {"agents": list(self._group_costs("agent_name", self.repository.list_cost_records()).values())}

    def get_model_cost_breakdown(self) -> dict:
        return {"models": list(self._group_costs("model_or_deployment", self.repository.list_cost_records(), include_provider=True).values())}

    def get_daily_cost_trend(self, days: int = 30) -> dict:
        cutoff = datetime.now(timezone.utc).date() - timedelta(days=max(days, 1) - 1)
        grouped: dict[str, dict] = defaultdict(lambda: {"date": "", "estimated_cost": 0.0, "total_tokens": 0, "call_count": 0})
        for record in self.repository.list_cost_records():
            date_key = self._date_key(record.get("created_at"))
            if not date_key or datetime.fromisoformat(date_key).date() < cutoff:
                continue
            grouped[date_key]["date"] = date_key
            grouped[date_key]["estimated_cost"] = round(grouped[date_key]["estimated_cost"] + record.get("estimated_total_cost", 0), 6)
            grouped[date_key]["total_tokens"] += record.get("total_tokens", 0)
            grouped[date_key]["call_count"] += 1
        return {"days": days, "trend": [grouped[key] for key in sorted(grouped)]}

    def get_top_expensive_cases(self, limit: int = 10) -> list[dict]:
        cases = [self.get_case_cost_breakdown(case_id) for case_id in self._group_costs("case_id", self.repository.list_cost_records())]
        return sorted(cases, key=lambda item: item.get("estimated_total_cost", 0), reverse=True)[:limit]

    def get_top_token_consuming_agents(self, limit: int = 10) -> list[dict]:
        agents = list(self._group_costs("agent_name", self.repository.list_cost_records()).values())
        return sorted(agents, key=lambda item: item.get("total_tokens", 0), reverse=True)[:limit]

    def get_cost_by_provider(self) -> dict:
        return {"providers": list(self._group_costs("ai_provider", self.repository.list_cost_records()).values())}

    def get_cost_efficiency_metrics(self) -> dict:
        summary = self.get_cost_summary()
        cases = self.case_repository.list_alerts()
        completed = [case for case in cases if case.get("status") in {"APPROVED", "HELD", "ESCALATED", "REJECTED", "CLOSED"}]
        reviewed = [case for case in cases if case.get("human_review")]
        escalated = [case for case in cases if case.get("status") == "ESCALATED"]
        usage = self.repository.list_token_usage_records()
        retry_cost = sum(record.get("estimated_total_cost", 0) for record in self.repository.list_cost_records() if record.get("metadata", {}).get("retry_count"))
        fallback_cost = sum(record.get("estimated_total_cost", 0) for record in self.repository.list_cost_records() if record.get("metadata", {}).get("fallback_used"))
        total_cost = summary["estimated_total_cost"]
        return {
            "estimated_cost_per_completed_investigation": self._safe_div(total_cost, len(completed)),
            "estimated_cost_per_human_reviewed_case": self._safe_div(total_cost, len(reviewed)),
            "estimated_cost_per_escalated_case": self._safe_div(total_cost, len(escalated)),
            "average_tokens_per_agent_execution": self._safe_div(sum(record.get("total_tokens", 0) for record in usage), len(usage)),
            "retry_cost_percentage": round((retry_cost / total_cost) * 100, 2) if total_cost else 0.0,
            "fallback_cost_percentage": round((fallback_cost / total_cost) * 100, 2) if total_cost else 0.0,
        }

    def recalculate_cost_records(self) -> dict:
        estimator = CostEstimator(CostMonitoringConfig())
        updated = []
        for usage in self.repository.list_token_usage_records():
            estimate = estimator.estimate_total_cost_for_usage(usage)
            updated.append(
                {
                    "cost_id": f"COST-RECALC-{usage['usage_id']}",
                    "usage_id": usage["usage_id"],
                    "case_id": usage.get("case_id"),
                    "agent_name": usage.get("agent_name"),
                    "operation_name": usage.get("operation_name"),
                    "ai_provider": usage.get("ai_provider"),
                    "model_or_deployment": usage.get("model_or_deployment"),
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "input_token_cost_per_1k": estimate["input_token_cost_per_1k"],
                    "output_token_cost_per_1k": estimate["output_token_cost_per_1k"],
                    "estimated_input_cost": estimate["estimated_input_cost"],
                    "estimated_output_cost": estimate["estimated_output_cost"],
                    "estimated_total_cost": estimate["estimated_total_cost"],
                    "currency": estimate["currency"],
                    "cost_source": "estimated_local",
                    "created_at": usage.get("created_at"),
                    "metadata": {"pricing_configured": estimate["pricing_configured"], "recalculated": True},
                }
            )
        self.repository.replace_cost_records(updated)
        return {"records_processed": len(updated), "cost_records_updated": len(updated), "pricing_configured": any((record.get("metadata") or {}).get("pricing_configured") for record in updated)}

    @staticmethod
    def _group_costs(key: str, records: list[dict], include_provider: bool = False) -> dict[str, dict]:
        grouped: dict[str, dict] = {}
        call_counts = Counter(record.get(key) or "UNKNOWN" for record in records)
        for record in records:
            name = record.get(key) or "UNKNOWN"
            item = grouped.setdefault(name, {"name": name, key: name, "total_tokens": 0, "estimated_cost": 0.0, "call_count": 0})
            item["total_tokens"] += record.get("total_tokens", 0)
            item["estimated_cost"] = round(item["estimated_cost"] + record.get("estimated_total_cost", 0), 6)
            item["call_count"] = call_counts[name]
            item["average_tokens_per_call"] = round(item["total_tokens"] / item["call_count"], 2) if item["call_count"] else 0.0
            item["average_cost_per_call"] = round(item["estimated_cost"] / item["call_count"], 6) if item["call_count"] else 0.0
            if include_provider:
                item["provider"] = record.get("ai_provider")
        return grouped

    @staticmethod
    def _token_counter(records: list[dict], key: str) -> dict:
        grouped = defaultdict(int)
        for record in records:
            grouped[record.get(key) or "UNKNOWN"] += record.get("total_tokens", 0)
        return dict(grouped)

    @staticmethod
    def _average(values: list[float | int]) -> float:
        return round(sum(values) / len(values), 6) if values else 0.0

    @staticmethod
    def _highest_key(grouped: dict[str, dict], field: str) -> str | None:
        if not grouped:
            return None
        return max(grouped.items(), key=lambda item: item[1].get(field, 0))[0]

    @staticmethod
    def _safe_div(value: float, denominator: int) -> float:
        return round(value / denominator, 6) if denominator else 0.0

    @staticmethod
    def _date_key(value: str | None) -> str | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            return None
