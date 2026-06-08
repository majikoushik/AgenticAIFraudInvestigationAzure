from app.compliance.compliance_redaction import redact_compliance_record


def test_compliance_redaction_masks_pii_and_raw_outputs() -> None:
    redacted = redact_compliance_record({"email": "person@example.com", "account": "123456789012", "raw_prompt": "secret prompt", "nested": {"authorization": "Bearer abc"}})

    assert redacted["email"] == "[REDACTED_EMAIL]"
    assert redacted["account"] == "[REDACTED_ACCOUNT]"
    assert redacted["raw_prompt"] == "[REDACTED]"
    assert redacted["nested"]["authorization"] == "[REDACTED]"
