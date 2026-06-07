from typing import Any

from agents.observability.agent_telemetry import track_agent_event


def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    try:
        from app.observability.observability_config import observability_config

        return round(
            (prompt_tokens / 1000) * observability_config.token_cost_input_per_1k
            + (completion_tokens / 1000) * observability_config.token_cost_output_per_1k,
            6,
        )
    except Exception:
        return 0.0


def track_llm_event(name: str, properties: dict[str, Any] | None = None, measurements: dict[str, float] | None = None) -> None:
    track_agent_event(name, properties, measurements)
