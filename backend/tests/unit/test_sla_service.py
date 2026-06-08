from datetime import UTC, datetime, timedelta

from app.assignment.sla_service import SlaService


def test_sla_due_date_calculated_by_priority() -> None:
    service = SlaService()
    assigned_at = datetime(2026, 6, 8, tzinfo=UTC)

    assert service.calculate_sla_due_at("CRITICAL", assigned_at) == assigned_at + timedelta(hours=4)


def test_sla_status_becomes_breached_after_due_time() -> None:
    service = SlaService()

    assert service.calculate_sla_status(datetime.now(UTC) - timedelta(minutes=1)) == "BREACHED"
