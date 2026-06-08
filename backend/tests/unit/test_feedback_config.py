from app.feedback.feedback_config import feedback_config


def test_feedback_config_loads_safe_defaults() -> None:
    summary = feedback_config.safe_summary()
    assert summary["enabled"] is True
    assert summary["mode"] == "local"
    assert "VERY_POOR" in summary["negative_ratings"]
