import json

from rag.ingestion.document_loader import DocumentLoader


def test_document_loader_loads_markdown_with_title(tmp_path) -> None:
    policy_path = tmp_path / "policy.md"
    policy_path.write_text("# Synthetic Policy\n\n## Review\n\nHuman review is required.", encoding="utf-8")

    document = DocumentLoader().load_markdown_file(policy_path)

    assert document.title == "Synthetic Policy"
    assert document.document_type == "POLICY"
    assert document.source_file == "policy.md"
    assert "Human review" in document.content


def test_document_loader_loads_json_as_searchable_text(tmp_path) -> None:
    case_path = tmp_path / "case.json"
    case_path.write_text(json.dumps({"case_id": "case-hist-test", "risk_indicators": ["HIGH_AMOUNT"]}), encoding="utf-8")

    documents = DocumentLoader().load_json_file(case_path, document_type="HISTORICAL_CASE")
    document = documents[0]

    assert document.title == "case-hist-test"
    assert document.document_type == "HISTORICAL_CASE"
    assert "case-hist-test" in document.content
