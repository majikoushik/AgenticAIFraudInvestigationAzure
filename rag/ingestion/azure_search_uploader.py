import json
import urllib.parse
import urllib.request

from rag.config.rag_config import rag_config


class AzureSearchUploader:
    def __init__(self, endpoint: str | None = None, admin_key: str | None = None) -> None:
        self.endpoint = (endpoint or rag_config.azure_search_endpoint).rstrip("/")
        self.admin_key = admin_key or rag_config.azure_search_admin_key

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.admin_key)

    def upload_chunks(self, index_name: str, chunks: list[dict], batch_size: int = 100) -> dict:
        if not self.is_configured:
            return {"chunks_uploaded": 0, "chunks_failed": len(chunks), "failed_chunk_ids": [chunk.get("chunk_id") for chunk in chunks]}
        uploaded = 0
        failed: list[str] = []
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            try:
                self._upload_batch(index_name, batch)
                uploaded += len(batch)
            except Exception:
                failed.extend(str(chunk.get("chunk_id")) for chunk in batch)
        return {"chunks_uploaded": uploaded, "chunks_failed": len(failed), "failed_chunk_ids": failed}

    def _upload_batch(self, index_name: str, chunks: list[dict]) -> None:
        actions = [{"@search.action": "mergeOrUpload", **chunk} for chunk in chunks]
        url = f"{self.endpoint}/indexes/{urllib.parse.quote(index_name)}/docs/index?api-version=2024-07-01"
        request = urllib.request.Request(
            url,
            data=json.dumps({"value": actions}).encode("utf-8"),
            headers={"Content-Type": "application/json", "api-key": self.admin_key},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30):
            pass
