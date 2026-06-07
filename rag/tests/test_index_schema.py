from rag.indexes.case_evidence_index_schema import build_case_evidence_index_schema
from rag.indexes.historical_case_index_schema import build_historical_case_index_schema
from rag.indexes.policy_index_schema import build_policy_index_schema


def _field_names(schema: dict) -> set[str]:
    return {field["name"] for field in schema["fields"]}


def test_policy_index_schema_contains_core_fields() -> None:
    schema = build_policy_index_schema("fraud-policies")

    assert schema["name"] == "fraud-policies"
    assert {"id", "content", "source_file", "content_vector"}.issubset(_field_names(schema))


def test_historical_case_index_schema_contains_core_fields() -> None:
    schema = build_historical_case_index_schema("historical-fraud-cases")

    assert schema["name"] == "historical-fraud-cases"
    assert {"historical_case_id", "risk_indicators", "outcome", "content_vector"}.issubset(_field_names(schema))


def test_case_evidence_index_schema_contains_core_fields() -> None:
    schema = build_case_evidence_index_schema("case-evidence")

    assert schema["name"] == "case-evidence"
    assert {"case_id", "evidence_type", "content", "content_vector"}.issubset(_field_names(schema))
