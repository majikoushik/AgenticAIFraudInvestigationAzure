def mask_account_number(account_number: str) -> str:
    if len(account_number) <= 4:
        return "****"
    return f"****{account_number[-4:]}"
