from agents.orchestration.guardrail_engine import GuardrailEngine


def test_guardrail_engine_flags_unsafe_recommendations() -> None:
    summary = {
        "case_overview": "The customer committed fraud and should receive a permanent account freeze.",
        "key_risk_indicators": [],
        "policy_references": [],
        "recommended_action": "escalate",
    }

    result = GuardrailEngine().validate_summary(summary)

    assert result["passed"] is False
    assert "DIRECT_ACCUSATION_NOT_ALLOWED" in result["safety_flags"]
    assert "PERMANENT_FREEZE_REQUIRES_HUMAN_REVIEW" in result["safety_flags"]
    assert "DECISION_WITHOUT_EVIDENCE" in result["safety_flags"]
