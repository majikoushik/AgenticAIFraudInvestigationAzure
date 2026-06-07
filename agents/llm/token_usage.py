from typing import Any


def add_usage(items: list[dict[str, Any]]) -> dict[str, int]:
    total = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    for item in items:
        usage = item.get("usage", {}) if isinstance(item, dict) else {}
        for key in total:
            total[key] += int(usage.get(key, 0) or 0)
    return total
