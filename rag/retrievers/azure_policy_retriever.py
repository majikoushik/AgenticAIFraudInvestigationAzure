import json
import os
import urllib.error
import urllib.parse
import urllib.request

from rag.ingestion.embedding_generator import EmbeddingGenerator
from rag.retrievers.base_retriever import RetrievalResult


class AzurePolicyRetriever:
    retrieval_mode = "azure_search"

    def __init__(self) -> None:
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "").rstrip("/")
        self.admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY", "")
        self.index_name = os.getenv("AZURE_SEARCH_POLICY_INDEX", "fraud-policies")
        self.embedding_generator = EmbeddingGenerator()

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.admin_key and self.index_name)

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        if not self.is_configured:
            raise RuntimeError("Azure AI Search policy retriever is not configured.")

        payload = {
            "search": query,
            "top": top_k,
            "select": "id,title,content,source_file,document_type,policy_name,section_title,tags,created_at",
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
                title=item.get("title", "Untitled policy"),
                content=item.get("content", ""),
                source_file=item.get("source_file", "azure-search"),
                score=float(item.get("@search.score", 0.0)),
                metadata={
                    "document_type": item.get("document_type", "policy"),
                    "policy_name": item.get("policy_name"),
                    "section_title": item.get("section_title"),
                    "tags": item.get("tags", []),
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
            raise RuntimeError(f"Azure AI Search policy retrieval failed: {exc}") from exc
