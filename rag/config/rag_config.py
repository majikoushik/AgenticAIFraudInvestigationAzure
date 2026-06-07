import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RagConfig:
    use_azure_search: bool = os.getenv("USE_AZURE_SEARCH", "false").lower() == "true"
    azure_search_endpoint: str = os.getenv("AZURE_SEARCH_ENDPOINT", "").rstrip("/")
    azure_search_admin_key: str = os.getenv("AZURE_SEARCH_ADMIN_KEY", "")
    azure_search_query_key: str = os.getenv("AZURE_SEARCH_QUERY_KEY", "")
    policy_index: str = os.getenv("AZURE_SEARCH_POLICY_INDEX", "fraud-policies")
    historical_case_index: str = os.getenv("AZURE_SEARCH_HISTORICAL_CASE_INDEX", "historical-fraud-cases")
    evidence_index: str = os.getenv("AZURE_SEARCH_EVIDENCE_INDEX", "case-evidence")
    semantic_config: str = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIG", "fraud-semantic-config")
    use_embeddings: bool = os.getenv("USE_AZURE_OPENAI_EMBEDDINGS", "false").lower() == "true"
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))
    top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    enable_hybrid_search: bool = os.getenv("RAG_ENABLE_HYBRID_SEARCH", "true").lower() == "true"
    enable_semantic_ranker: bool = os.getenv("RAG_ENABLE_SEMANTIC_RANKER", "false").lower() == "true"

    @property
    def azure_search_configured(self) -> bool:
        return bool(self.azure_search_endpoint and (self.azure_search_query_key or self.azure_search_admin_key))

    @property
    def retrieval_mode(self) -> str:
        return "azure_ai_search" if self.use_azure_search and self.azure_search_configured else "local"


rag_config = RagConfig()
