from app.observability.observability_config import ObservabilityConfig


def test_observability_config_safe_defaults(monkeypatch) -> None:
    monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)

    config = ObservabilityConfig()

    assert config.enabled is True
    assert config.mode == "local"
    assert config.log_prompts is False
    assert config.log_responses is False
    assert config.log_pii is False
    assert config.safe_summary()["application_insights"] == "missing"
