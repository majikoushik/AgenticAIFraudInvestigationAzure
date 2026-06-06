from pydantic import BaseModel


class Device(BaseModel):
    device_id: str
    customer_id: str
    device_type: str
    trusted: bool
    last_seen_ip: str
    last_seen_country: str
    first_seen: str
