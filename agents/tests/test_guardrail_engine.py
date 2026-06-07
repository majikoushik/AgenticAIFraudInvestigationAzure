from agents.safety.guardrail_engine import GuardrailEngine


def test_guardrail_engine_enforces_human_review_and_flags_output() -> None:
    result = GuardrailEngine().validate_summary(
        {
            "case_overview": "The customer is fraudulent.",
            "recommended_action": "HOLD",
            "confidence_level": "HIGH",
            "missing_evidence": [],
            "policy_references": [{"source_filename": "new-beneficiary-policy.md"}],
            "human_review_required": True,
        }
    )

    assert result["requires_human_review"] is True
    assert "DIRECT_ACCUSATION_NOT_ALLOWED" in result["safety_flags"]
