from rag.ingestion.document_loader import LoadedDocument
from rag.ingestion.metadata_extractor import MetadataExtractor


def test_metadata_extractor_adds_policy_defaults() -> None:
    document = LoadedDocument(
        source_file="policy.md",
        title="Synthetic Policy",
        document_type="POLICY",
        content="# Synthetic Policy\n\n## Human Review\n\nReview high-value transfers.",
    )

    metadata = MetadataExtractor().extract(document)

    assert metadata["policy_name"] == "Synthetic Policy"
    assert metadata["section_title"] == "Human Review"
    assert "high-value" in metadata["tags"]


def test_metadata_extractor_adds_historical_case_defaults() -> None:
    document = LoadedDocument(
        source_file="historical.json",
        title="case-hist-test",
        document_type="HISTORICAL_CASE",
        content="new device high amount",
        metadata={"case_id": "case-hist-test", "risk_indicators": ["HIGH_AMOUNT"]},
    )

    metadata = MetadataExtractor().extract(document)

    assert metadata["historical_case_id"] == "case-hist-test"
    assert metadata["case_type"] == "historical_fraud_case"
    assert metadata["risk_indicators"] == ["HIGH_AMOUNT"]
