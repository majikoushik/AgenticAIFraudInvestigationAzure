from app.feedback.feedback_sanitizer import sanitize_ai_output_snapshot, sanitize_feedback_payload


def test_feedback_sanitizer_removes_sensitive_fields() -> None:
    clean = sanitize_feedback_payload({"raw_prompt": "secret prompt", "token": "abc", "comment": "Call me at 5555555555", "nested": {"chain_of_thought": "hidden", "safe": "ok"}})
    assert "raw_prompt" not in clean
    assert "token" not in clean
    assert "chain_of_thought" not in clean["nested"]
    assert clean["comment"] == "Call me at [masked-number]"


def test_snapshot_sanitizer_uses_allowlist() -> None:
    clean = sanitize_ai_output_snapshot({"recommended_action": "HOLD", "raw_response": "hidden", "extra": "drop"})
    assert clean == {"recommended_action": "HOLD"}
