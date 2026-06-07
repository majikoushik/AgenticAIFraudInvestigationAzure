from app.cost.cost_repository import CostRepository
from app.cost.cost_service import CostService


def _seed(repository: CostRepository) -> None:
    repository.append_token_usage_record({"usage_id": "TOK-1", "case_id": "case-1", "agent_name": "AgentA", "operation_name": "op", "ai_provider": "local", "model_or_deployment": "model-a", "prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150, "created_at": "2026-01-01T00:00:00Z", "metadata": {}})
    repository.append_cost_record({"cost_id": "COST-1", "usage_id": "TOK-1", "case_id": "case-1", "agent_name": "AgentA", "operation_name": "op", "ai_provider": "local", "model_or_deployment": "model-a", "prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150, "estimated_total_cost": 1.25, "currency": "USD", "created_at": "2026-01-01T00:00:00Z", "metadata": {"pricing_configured": True}})


def test_cost_service_returns_summary_with_no_records(tmp_path) -> None:
    service = CostService(CostRepository(str(tmp_path / "cost_records.json")))

    assert service.get_cost_summary()["total_tokens"] == 0


def test_cost_service_aggregates_case_agent_model_and_trend(tmp_path) -> None:
    repository = CostRepository(str(tmp_path / "cost_records.json"))
    _seed(repository)
    service = CostService(repository)

    assert service.get_cost_summary()["estimated_total_cost"] == 1.25
    assert service.get_case_cost_breakdown("case-1")["estimated_total_cost"] == 1.25
    assert service.get_agent_cost_breakdown()["agents"][0]["total_tokens"] == 150
    assert service.get_model_cost_breakdown()["models"][0]["model_or_deployment"] == "model-a"
    assert service.get_daily_cost_trend(days=3650)["trend"][0]["estimated_cost"] == 1.25


def test_cost_service_recalculates_cost_records(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DEFAULT_INPUT_TOKEN_COST_PER_1K", "0.10")
    repository = CostRepository(str(tmp_path / "cost_records.json"))
    repository.append_token_usage_record({"usage_id": "TOK-1", "case_id": "case-1", "agent_name": "AgentA", "operation_name": "op", "ai_provider": "local", "model_or_deployment": "model-a", "prompt_tokens": 1000, "completion_tokens": 0, "total_tokens": 1000, "created_at": "2026-01-01T00:00:00Z", "metadata": {}})

    result = CostService(repository).recalculate_cost_records()

    assert result["cost_records_updated"] == 1
    assert repository.list_cost_records()[0]["estimated_total_cost"] == 0.1
