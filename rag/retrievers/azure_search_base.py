import json
import urllib.error
import urllib.parse
import urllib.request

from rag.config.rag_config import rag_config
from rag.ingestion.embedding_generator import EmbeddingGenerator
from rag.retrievers.base_retriever import RetrievalResult


class AzureSearchRetrieverBase:
    retrieval_mode = "azure_ai_search"

    def __init__(self, index_name: str) -> None:
        self.endpoint = rag_config.azure_search_endpoint
        self.query_key = rag_config.azure_search_query_key or rag_config.azure_search_admin_key
        self.index_name = index_name
        self.embedding_generator = EmbeddingGenerator()

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.query_key and self.index_name)

    def search(self, query: str, top_k: int = 5, filters: dict | None = None) -> list[RetrievalResult]:
        if not self.is_configured:
            raise RuntimeError("Azure AI Search retriever is not configured.")
        payload = {"search": query, "top": top_k, "select": "*"}
        filter_text = self._build_filter(filters or {})
        if filter_text:
            payload["filter"] = filter_text
        vector = self.embedding_generator.generate(query)
        if vector and rag_config.enable_hybrid_search:
            payload["vectorQueries"] = [{"kind": "vector", "vector": vector, "fields": "content_vector", "k": top_k}]
        response = self._post_search(payload)
        return [self._to_result(item) for item in response.get("value", [])]

    def _post_search(self, payload: dict) -> dict:
        url = f"{self.endpoint}/indexes/{urllib.parse.quote(self.index_name)}/docs/search?api-version=2024-07-01"
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "api-key": self.query_key},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Azure AI Search retrieval failed: {exc}") from exc

    def _to_result(self, item: dict) -> RetrievalResult:
        metadata = self._metadata(item)
        chunk_id = item.get("chunk_id") or item.get("id", "")
        return RetrievalResult(
            id=item.get("id", chunk_id),
            title=item.get("title", "Untitled"),
            content=item.get("content", ""),
            source_file=item.get("source_file", "azure-search"),
            source_path=item.get("source_path", ""),
            document_type=item.get("document_type", ""),
            score=float(item.get("@search.score", 0.0)),
            reranker_score=float(item.get("@search.rerankerScore", 0.0) or 0.0),
            metadata=metadata,
            citation={"source": item.get("source_file"), "title": item.get("title"), "section": item.get("section_title"), "chunk_id": chunk_id},
        )

    @staticmethod
    def _metadata(item: dict) -> dict:
        metadata = dict(item)
        metadata.pop("content", None)
        metadata["retrieval_mode"] = "azure_ai_search"
        return metadata

    @staticmethod
    def _build_filter(filters: dict) -> str:
        clauses = []
        for key, value in filters.items():
            if value is None:
                continue
            safe_value = str(value).replace("'", "''")
            clauses.append(f"{key} eq '{safe_value}'")
        return " and ".join(clauses)
