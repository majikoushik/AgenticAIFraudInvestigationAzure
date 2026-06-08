from app.compliance.archival_service import archival_service


def test_archival_service_dry_run_does_not_modify_source() -> None:
    result = archival_service.archive_record("FRAUD_CASE", "case-001", "tester", dry_run=True)

    assert result["dry_run"] is True
    assert result["results"][0]["would_archive"] is True
