from pathlib import Path

from rag.retrievers.local_policy_retriever import LocalPolicyRetriever


def test_local_policy_retriever_returns_consistent_structure(tmp_path: Path) -> None:
    policy = tmp_path / "new-beneficiary-policy.md"
    policy.write_text(
        "# New Beneficiary Policy\n\n## Review\n\nNew beneficiary transfers require human review.",
        encoding="utf-8",
    )

    results = LocalPolicyRetriever(tmp_path).search("new beneficiary review", top_k=2)

    assert len(results) == 1
    assert results[0].title == "New Beneficiary Policy"
    assert results[0].source_file == "new-beneficiary-policy.md"
    assert results[0].metadata["section_title"] == "Review"
