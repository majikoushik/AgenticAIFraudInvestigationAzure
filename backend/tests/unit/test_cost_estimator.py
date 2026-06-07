from app.cost.cost_config import CostMonitoringConfig
from app.cost.cost_estimator import CostEstimator


def test_cost_estimator_calculates_input_output_total(monkeypatch) -> None:
    monkeypatch.setenv("DEFAULT_INPUT_TOKEN_COST_PER_1K", "0.10")
    monkeypatch.setenv("DEFAULT_OUTPUT_TOKEN_COST_PER_1K", "0.20")

    result = CostEstimator(CostMonitoringConfig()).estimate_llm_cost("unknown-model", 1000, 500)

    assert result["estimated_input_cost"] == 0.10
    assert result["estimated_output_cost"] == 0.10
    assert result["estimated_total_cost"] == 0.20
    assert result["pricing_configured"] is True


def test_cost_estimator_handles_zero_pricing_safely() -> None:
    result = CostEstimator(CostMonitoringConfig()).estimate_llm_cost("unknown-model", None, None)

    assert result["estimated_total_cost"] == 0.0
    assert result["pricing_configured"] is False
    assert result["warning"]
