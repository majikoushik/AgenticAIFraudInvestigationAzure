from agents.safety.pii_redactor import PiiRedactor


def test_pii_redactor_masks_account_numbers_and_email() -> None:
    redactor = PiiRedactor()
    data = {"case_id": "case-001", "customer_id": "cust-001", "account_number": "1234567890123456", "email": "user@example.com"}

    redacted = redactor.redact_dict(data)

    assert redacted["case_id"] == "case-001"
    assert redacted["customer_id"] == "***MASKED_CUSTOMER_ID***"
    assert redacted["account_number"] == "****3456"
    assert redacted["email"] == "u***@example.com"
