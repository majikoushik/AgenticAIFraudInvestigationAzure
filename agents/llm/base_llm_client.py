from abc import ABC, abstractmethod
from typing import Any


def empty_usage() -> dict[str, int]:
    return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def llm_response(
    provider: str,
    model: str = "",
    content: str = "",
    json_payload: dict[str, Any] | None = None,
    usage: dict[str, int] | None = None,
    latency_ms: float = 0.0,
    finish_reason: str = "unknown",
    error: str | None = None,
    fallback_used: bool = False,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "model": model,
        "content": content,
        "json": json_payload or {},
        "usage": usage or empty_usage(),
        "latency_ms": round(latency_ms, 2),
        "finish_reason": finish_reason,
        "error": error,
        "fallback_used": fallback_used,
    }


class BaseLLMClient(ABC):
    provider_name: str
    model_name: str = ""

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        json_schema: dict | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def get_provider_name(self) -> str:
        return self.provider_name
