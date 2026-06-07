from app.cost.cost_config import CostMonitoringConfig


def test_cost_config_loads_safe_defaults(monkeypatch) -> None:
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "synthetic-subscription")
    config = CostMonitoringConfig()

    summary = config.safe_summary()

    assert summary["cost_monitoring_enabled"] is True
    assert summary["pricing_configured"] is False
    assert summary["azure_subscription_configured"] is True
    assert "synthetic-subscription" not in summary.values()


def test_cost_config_returns_model_specific_rate(monkeypatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_GPT4O_MINI_INPUT_COST_PER_1K", "0.10")
    monkeypatch.setenv("AZURE_OPENAI_GPT4O_MINI_OUTPUT_COST_PER_1K", "0.20")

    rate = CostMonitoringConfig().get_rate_for_model("gpt-4o-mini")

    assert rate["input_token_cost_per_1k"] == 0.10
    assert rate["output_token_cost_per_1k"] == 0.20
    assert rate["pricing_configured"] is True
