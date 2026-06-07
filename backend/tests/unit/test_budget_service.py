from datetime import datetime, timezone

from app.cost.budget_service import BudgetService
from app.cost.cost_config import cost_monitoring_config
from app.cost.cost_repository import CostRepository


def test_budget_service_returns_not_configured_when_limits_zero(tmp_path) -> None:
    original = (cost_monitoring_config.daily_budget_limit, cost_monitoring_config.monthly_budget_limit, cost_monitoring_config.token_daily_limit)
    object.__setattr__(cost_monitoring_config, "daily_budget_limit", 0)
    object.__setattr__(cost_monitoring_config, "monthly_budget_limit", 0)
    object.__setattr__(cost_monitoring_config, "token_daily_limit", 0)
    try:
        status = BudgetService(CostRepository(str(tmp_path / "cost_records.json"))).get_budget_status()
    finally:
        object.__setattr__(cost_monitoring_config, "daily_budget_limit", original[0])
        object.__setattr__(cost_monitoring_config, "monthly_budget_limit", original[1])
        object.__setattr__(cost_monitoring_config, "token_daily_limit", original[2])

    assert status["status"] == "NOT_CONFIGURED"


def test_budget_service_returns_exceeded(tmp_path) -> None:
    original = cost_monitoring_config.daily_budget_limit
    object.__setattr__(cost_monitoring_config, "daily_budget_limit", 1)
    repository = CostRepository(str(tmp_path / "cost_records.json"))
    today = datetime.now(timezone.utc).date().isoformat()
    repository.append_cost_record({"cost_id": "COST-1", "usage_id": "TOK-1", "case_id": "case-1", "agent_name": "Agent", "operation_name": "op", "ai_provider": "local", "model_or_deployment": "model", "total_tokens": 1, "estimated_total_cost": 2.0, "created_at": f"{today}T00:00:00Z", "metadata": {}})

    try:
        status = BudgetService(repository).get_budget_status()
    finally:
        object.__setattr__(cost_monitoring_config, "daily_budget_limit", original)

    assert status["status"] == "EXCEEDED"
