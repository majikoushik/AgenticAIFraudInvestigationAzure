from typing import Any
from math import ceil


def add_usage(items: list[dict[str, Any]]) -> dict[str, int]:
    total = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    for item in items:
        usage = item.get("usage", {}) if isinstance(item, dict) else {}
        for key in total:
            total[key] += int(usage.get(key, 0) or 0)
    return total


def estimate_tokens_from_text(text: str) -> int:
    return ceil(len(text or "") / 4)


def build_usage(prompt: str = "", completion: str = "", prompt_tokens: int | None = None, completion_tokens: int | None = None) -> dict[str, int]:
    prompt_count = int(prompt_tokens if prompt_tokens is not None else estimate_tokens_from_text(prompt))
    completion_count = int(completion_tokens if completion_tokens is not None else estimate_tokens_from_text(completion))
    return {"prompt_tokens": prompt_count, "completion_tokens": completion_count, "total_tokens": prompt_count + completion_count}
