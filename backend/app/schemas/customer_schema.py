from pydantic import BaseModel


class CustomerProfile(BaseModel):
    customer_id: str
    display_name: str
    account_number_masked: str
    segment: str
    risk_tier: str
    home_country: str
    account_opened_date: str
    average_transaction_amount: float
