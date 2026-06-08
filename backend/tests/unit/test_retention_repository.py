from app.compliance.retention_repository import retention_repository


def test_retention_repository_lists_fraud_cases() -> None:
    records = retention_repository.list_records_by_category("FRAUD_CASE")

    assert records
    assert retention_repository.get_record_id(records[0], "FRAUD_CASE")
