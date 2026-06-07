from agents.observability.llm_telemetry import estimate_cost, track_llm_event


def test_llm_telemetry_estimates_cost_and_records_event() -> None:
    assert estimate_cost(100, 50) >= 0
    track_llm_event("LLM_TOKEN_USAGE_RECORDED", {"provider": "local"}, {"total_tokens": 150})
