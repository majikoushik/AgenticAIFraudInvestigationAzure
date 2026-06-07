from agents.safety.citation_validator import CitationValidator


def test_citation_validator_flags_invented_citation() -> None:
    result = CitationValidator().validate(
        [{"source_filename": "invented.md"}],
        [{"source_filename": "new-beneficiary-policy.md"}],
    )

    assert result["passed"] is False
    assert result["citation_issues"]
