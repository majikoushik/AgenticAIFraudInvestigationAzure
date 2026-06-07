from agents.llm.token_usage import add_usage, build_usage, estimate_tokens_from_text


def test_estimate_tokens_from_text_uses_character_fallback() -> None:
    assert estimate_tokens_from_text("abcdefgh") == 2


def test_build_usage_calculates_total_tokens_without_raw_text_storage() -> None:
    usage = build_usage(prompt="abcdefgh", completion="abcd")

    assert usage == {"prompt_tokens": 2, "completion_tokens": 1, "total_tokens": 3}


def test_add_usage_sums_llm_response_metadata() -> None:
    total = add_usage([{"usage": {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5}}, {"usage": {"prompt_tokens": 4, "completion_tokens": 1, "total_tokens": 5}}])

    assert total["total_tokens"] == 10
