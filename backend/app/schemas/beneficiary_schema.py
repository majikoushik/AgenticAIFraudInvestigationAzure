from pydantic import BaseModel


class Beneficiary(BaseModel):
    beneficiary_id: str
    customer_id: str
    display_name: str
    relationship_type: str
    bank_country: str
    first_seen: str
    risk_note: str
