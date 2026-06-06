from pathlib import Path

from rag.retrievers.hybrid_retriever import HybridPolicyRetriever
from rag.retrievers.local_policy_retriever import LocalPolicyRetriever


def test_hybrid_retriever_uses_local_when_azure_config_missing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("USE_AZURE_SEARCH", "true")
    monkeypatch.delenv("AZURE_SEARCH_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_SEARCH_ADMIN_KEY", raising=False)
    policy = tmp_path / "policy.md"
    policy.write_text("# Fraud Policy\n\n## Review\n\nHigh value transfer review.", encoding="utf-8")

    retriever = HybridPolicyRetriever(local_retriever=LocalPolicyRetriever(tmp_path))
    results = retriever.search("high value transfer", top_k=1)

    assert retriever.retrieval_mode == "local"
    assert len(results) == 1
