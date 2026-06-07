from rag.retrievers.local_case_evidence_retriever import LocalCaseEvidenceRetriever
from rag.retrievers.local_historical_case_retriever import LocalHistoricalCaseRetriever


def test_local_historical_case_retriever_returns_citation_ready_result() -> None:
    results = LocalHistoricalCaseRetriever().search("HIGH_AMOUNT NEW_BENEFICIARY", top_k=2)

    assert results
    assert results[0].source_file == "historical_cases.json"
    assert results[0].metadata["retrieval_mode"] == "local"


def test_local_case_evidence_retriever_searches_synthetic_files() -> None:
    results = LocalCaseEvidenceRetriever().search("new beneficiary high amount", top_k=3)

    assert results
    assert results[0].document_type == "CASE_EVIDENCE"
    assert results[0].source_file.endswith(".json")
