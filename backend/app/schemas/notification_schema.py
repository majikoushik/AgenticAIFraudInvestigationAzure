from datetime import datetime

from pydantic import BaseModel


class NotificationEvent(BaseModel):
    notification_id: str
    channel: str
    alert_id: str | None = None
    incident_id: str | None = None
    severity: str
    title: str
    message: str
    sent_at: datetime
    status: str
    error_message: str | None = None
