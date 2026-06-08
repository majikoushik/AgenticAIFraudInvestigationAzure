from app.assignment.assignment_config import assignment_config


def test_assignment_config_safe_summary_has_no_secrets() -> None:
    summary = assignment_config.safe_summary()

    assert summary["enabled"] is True
    assert summary["mode"] == "local"
    assert summary["sla_hours_by_priority"]["CRITICAL"] == 4
