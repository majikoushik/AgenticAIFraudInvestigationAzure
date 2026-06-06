from pathlib import Path
import sys

from app.schemas.rag_schema import PolicySearchResponse


def _ensure_project_root_on_path() -> None:
    project_root = Path(__file__).resolve().parents[3]
    project_root_text = str(project_root)
    if project_root_text not in sys.path:
        sys.path.append(project_root_text)


_ensure_project_root_on_path()

from rag.retrievers.citation_builder import build_policy_reference  # noqa: E402
from rag.retrievers.hybrid_retriever import HybridPolicyRetriever  # noqa: E402


class RagService:
    def __init__(self, retriever: HybridPolicyRetriever | None = None) -> None:
        self.retriever = retriever or HybridPolicyRetriever()

    def search_policies(self, query: str, top_k: int = 3) -> PolicySearchResponse:
        results = self.retriever.search(query, top_k=top_k)
        return PolicySearchResponse(
            query=query,
            retrieval_mode=self.retriever.retrieval_mode,
            results=[build_policy_reference(result) for result in results],
        )
