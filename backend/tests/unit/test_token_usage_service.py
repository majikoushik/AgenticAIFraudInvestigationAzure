from app.cost.cost_config import CostMonitoringConfig
from app.cost.cost_estimator import CostEstimator
from app.cost.cost_repository import CostRepository
from app.cost.token_usage_service import TokenUsageService


def test_token_usage_service_records_usage_and_cost(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DEFAULT_INPUT_TOKEN_COST_PER_1K", "0.10")
    monkeypatch.setenv("DEFAULT_OUTPUT_TOKEN_COST_PER_1K", "0.20")
    repository = CostRepository(str(tmp_path / "cost_records.json"))
    service = TokenUsageService(repository, CostEstimator(CostMonitoringConfig()))

    result = service.record_token_usage("case-1", "CaseSummaryAgent", "generate", "local", "local-model", 1000, 500, metadata={"customer_name": "Fake Person"})

    assert result["token_usage_record"]["total_tokens"] == 1500
    assert result["token_usage_record"]["metadata"]["customer_name"] == "***MASKED***"
    assert result["cost_record"]["estimated_total_cost"] == 0.20
    assert len(repository.list_cost_records()) == 1


def test_token_usage_service_estimates_tokens_from_text() -> None:
    assert TokenUsageService.estimate_tokens_from_text("abcdefgh") == 2
