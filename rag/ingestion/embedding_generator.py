import json
import os
import urllib.error
import urllib.request


class EmbeddingGenerator:
    def __init__(self) -> None:
        self.enabled = os.getenv("USE_AZURE_OPENAI_EMBEDDINGS", "false").lower() == "true"
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

    @property
    def is_configured(self) -> bool:
        return self.is_available()

    def is_available(self) -> bool:
        return bool(self.enabled and self.endpoint and self.api_key and self.deployment)

    def generate_embedding(self, text: str) -> list[float] | None:
        if not self.is_available():
            return None

        url = (
            f"{self.endpoint}/openai/deployments/{self.deployment}/embeddings"
            f"?api-version={self.api_version}"
        )
        request = urllib.request.Request(
            url,
            data=json.dumps({"input": text[:8000]}).encode("utf-8"),
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
            return None

    def generate_embeddings(self, texts: list[str]) -> list[list[float] | None]:
        return [self.generate_embedding(text) for text in texts]

    def generate(self, text: str) -> list[float]:
        return self.generate_embedding(text) or []
