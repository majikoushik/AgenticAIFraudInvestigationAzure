from agents.safety.output_validator import OutputValidator


def test_output_validator_rejects_missing_human_review() -> None:
    result = OutputValidator().validate_summary({"recommended_action": "HOLD", "confidence_level": "HIGH", "missing_evidence": [], "policy_references": [{}]})

    assert "HUMAN_REVIEW_REQUIRED" in result["validation_errors"]


def test_output_validator_rejects_direct_accusation() -> None:
    result = OutputValidator().validate_summary(
        {
            "recommended_action": "HOLD",
            "confidence_level": "HIGH",
            "missing_evidence": [],
            "human_review_required": True,
            "policy_references": [{}],
            "case_overview": "The customer committed fraud.",
        }
    )

    assert "DIRECT_ACCUSATION_NOT_ALLOWED" in result["safety_flags"]
