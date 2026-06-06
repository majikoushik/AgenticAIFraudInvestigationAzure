import json
import os
import urllib.error
import urllib.request


class EmbeddingGenerator:
    def __init__(self) -> None:
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key and self.deployment)

    def generate(self, text: str) -> list[float]:
        if not self.is_configured:
            return []

        url = (
            f"{self.endpoint}/openai/deployments/{self.deployment}/embeddings"
            "?api-version=2024-02-01"
        )
        request = urllib.request.Request(
            url,
            data=json.dumps({"input": text}).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "api-key": self.api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return payload["data"][0]["embedding"]
        except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Azure OpenAI embedding request failed: {exc}") from exc
