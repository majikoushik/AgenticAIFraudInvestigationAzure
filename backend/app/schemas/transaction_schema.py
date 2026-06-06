from pydantic import BaseModel


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    merchant: str
    merchant_country: str
    timestamp: str
    channel: str
    payment_method: str
    beneficiary_id: str | None = None
    device_id: str | None = None
