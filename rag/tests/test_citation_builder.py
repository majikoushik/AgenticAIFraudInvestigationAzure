from rag.retrievers.base_retriever import RetrievalResult
from rag.retrievers.citation_builder import build_policy_reference


def test_citation_builder_adds_policy_reference_fields() -> None:
    result = RetrievalResult(
        title="Fraud Policy",
        content="Human review is required.",
        source_file="fraud-policy.md",
        score=2.0,
        metadata={"section_title": "Human Review"},
    )

    citation = build_policy_reference(result)

    assert citation["title"] == "Fraud Policy"
    assert citation["source_filename"] == "fraud-policy.md"
    assert citation["matched_section"] == "Human Review"
    assert citation["snippet"] == "Human review is required."
    assert citation["retrieval_mode"] == "local"
    assert citation["citation"]["chunk_id"] == ""
    assert citation["explanation"]
