from app.compliance.data_classification_registry import data_classification_registry


def test_data_classification_registry_returns_fraud_case_classification() -> None:
    assert data_classification_registry.get_classification("FRAUD_CASE") == "RESTRICTED"
    assert data_classification_registry.is_restricted("FRAUD_CASE") is True
