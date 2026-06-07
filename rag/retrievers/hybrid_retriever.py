import os

from rag.retrievers.azure_policy_retriever import AzurePolicyRetriever
from rag.retrievers.base_retriever import RetrievalResult
from rag.retrievers.local_policy_retriever import LocalPolicyRetriever


class HybridPolicyRetriever:
    def __init__(
        self,
        local_retriever: LocalPolicyRetriever | None = None,
        azure_retriever: AzurePolicyRetriever | None = None,
    ) -> None:
        self.local_retriever = local_retriever or LocalPolicyRetriever()
        self.azure_retriever = azure_retriever or AzurePolicyRetriever()
        self.last_retrieval_mode = "local"

    @property
    def retrieval_mode(self) -> str:
        return self.last_retrieval_mode

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        if self._use_azure():
            self.last_retrieval_mode = "azure_ai_search"
            return self.azure_retriever.search(query, top_k)

        self.last_retrieval_mode = "local"
        return self.local_retriever.search(query, top_k)

    def _use_azure(self) -> bool:
        return os.getenv("USE_AZURE_SEARCH", "false").lower() == "true" and self.azure_retriever.is_configured
