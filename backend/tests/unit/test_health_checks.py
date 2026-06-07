from app.observability.health_checks import run_health_checks


def test_health_checks_return_safe_status() -> None:
    details = run_health_checks()

    assert details["status"] in {"ok", "degraded", "unhealthy"}
    assert "application_insights" in details["checks"]
    assert "connection_string" not in str(details).lower()
