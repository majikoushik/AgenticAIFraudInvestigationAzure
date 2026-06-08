from app.compliance.compliance_report_service import compliance_report_service


def test_compliance_report_service_returns_summary() -> None:
    summary = compliance_report_service.get_compliance_summary()

    assert "total_records_by_category" in summary
    assert summary["policy_count"] >= 1
