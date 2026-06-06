import json
import os
import urllib.error
import urllib.request
from typing import Any


class SearchIndexUploader:
    def __init__(self, endpoint: str | None = None, admin_key: str | None = None) -> None:
        self.endpoint = (endpoint or os.getenv("AZURE_SEARCH_ENDPOINT", "")).rstrip("/")
        self.admin_key = admin_key or os.getenv("AZURE_SEARCH_ADMIN_KEY", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.admin_key)

    def upload_documents(self, index_name: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
        if not self.is_configured:
            raise RuntimeError("Azure AI Search endpoint/admin key are not configured.")
        if not documents:
            return {"uploaded": 0, "index": index_name}

        actions = [{**document, "@search.action": "upload"} for document in documents]
        return self._post(f"/indexes/{index_name}/docs/index", {"value": actions})

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.endpoint}{path}?api-version=2024-07-01"
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
            raise RuntimeError(f"Azure AI Search upload failed: {exc}") from exc
