from agents.llm.llm_response_parser import LLMResponseParser


def test_llm_response_parser_handles_valid_json() -> None:
    result = LLMResponseParser().parse_json('{"recommended_action": "hold"}')

    assert result["parsed"]["recommended_action"] == "hold"
    assert result["errors"] == []


def test_llm_response_parser_handles_invalid_json() -> None:
    result = LLMResponseParser().parse_json("not json")

    assert result["parsed"] == {}
    assert "invalid_json" in result["errors"]
