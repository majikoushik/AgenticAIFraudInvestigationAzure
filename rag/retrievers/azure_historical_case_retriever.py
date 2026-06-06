import json
import os
import urllib.error
import urllib.parse
import urllib.request

from rag.ingestion.embedding_generator import EmbeddingGenerator
from rag.retrievers.base_retriever import RetrievalResult


class AzureHistoricalCaseRetriever:
    retrieval_mode = "azure_search"

    def __init__(self) -> None:
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "").rstrip("/")
        self.admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY", "")
        self.index_name = os.getenv("AZURE_SEARCH_CASE_INDEX", "historical-fraud-cases")
        self.embedding_generator = EmbeddingGenerator()

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.admin_key and self.index_name)

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        if not self.is_configured:
            raise RuntimeError("Azure AI Search historical case retriever is not configured.")

        payload = {
            "search": query,
            "top": top_k,
            "select": "id,case_id,title,content,source_file,case_type,risk_indicators,outcome,created_at",
        }
        vector = self.embedding_generator.generate(query) if self.embedding_generator.is_configured else []
        if vector:
            payload["vectorQueries"] = [
                {
                    "kind": "vector",
                    "vector": vector,
                    "fields": "content_vector",
                    "k": top_k,
                }
            ]

        response = self._post_search(payload)
        return [
            RetrievalResult(
                title=item.get("title", "Historical case"),
                content=item.get("content", ""),
                source_file=item.get("source_file", "azure-search"),
                score=float(item.get("@search.score", 0.0)),
                metadata={
                    "case_id": item.get("case_id"),
                    "case_type": item.get("case_type"),
                    "risk_indicators": item.get("risk_indicators", []),
                    "outcome": item.get("outcome", "unknown"),
                    "created_at": item.get("created_at"),
                    "retrieval_mode": self.retrieval_mode,
                },
            )
            for item in response.get("value", [])
        ]

    def _post_search(self, payload: dict) -> dict:
        index_name = urllib.parse.quote(self.index_name)
        url = f"{self.endpoint}/indexes/{index_name}/docs/search?api-version=2024-07-01"
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "api-key": self.admin_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Azure AI Search historical case retrieval failed: {exc}") from exc
