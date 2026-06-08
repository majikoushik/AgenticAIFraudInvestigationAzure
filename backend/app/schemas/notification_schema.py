from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.constants import NotificationChannel, NotificationEventType, NotificationPriority, NotificationRecipientType, NotificationStatus


class NotificationDeliveryRecord(BaseModel):
    channel: NotificationChannel
    status: NotificationStatus
    attempt_count: int = 1
    last_attempt_at: datetime | None = None
    error_message: str | None = None
    sent_at: datetime | None = None


class NotificationCreate(BaseModel):
    event_type: NotificationEventType
    priority: NotificationPriority = NotificationPriority.INFO
    title: str
    message: str
    recipient_type: NotificationRecipientType
    recipient_id: str | None = None
    recipient_role: str | None = None
    recipient_team: str | None = None
    channels: list[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.IN_APP, NotificationChannel.LOCAL])
    case_id: str | None = None
    alert_id: str | None = None
    incident_id: str | None = None
    correlation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(NotificationCreate):
    notification_id: str
    status: NotificationStatus
    read: bool = False
    archived: bool = False
    delivery_records: list[NotificationDeliveryRecord] = Field(default_factory=list)
    created_at: datetime
    sent_at: datetime | None = None
    read_at: datetime | None = None
    archived_at: datetime | None = None


class NotificationListResponse(BaseModel):
    count: int
    notifications: list[NotificationResponse]


class NotificationPreference(BaseModel):
    user_id: str
    role: str | None = None
    team: str | None = None
    enabled: bool = True
    channels: list[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.IN_APP, NotificationChannel.LOCAL])
    event_preferences: dict[str, dict[str, Any]] = Field(default_factory=dict)
    quiet_hours: dict[str, Any] = Field(default_factory=lambda: {"enabled": False, "start": "22:00", "end": "07:00", "timezone": "Asia/Kolkata"})
    updated_at: datetime | None = None


class NotificationTemplate(BaseModel):
    template_id: str
    event_type: NotificationEventType
    title_template: str
    message_template: str
    default_priority: NotificationPriority = NotificationPriority.INFO
    default_channels: list[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.IN_APP, NotificationChannel.LOCAL])
    enabled: bool = True


class NotificationDispatchRequest(BaseModel):
    notification_id: str


class NotificationMarkReadRequest(BaseModel):
    read: bool = True


class NotificationBulkUpdateRequest(BaseModel):
    notification_ids: list[str]
    read: bool | None = None
    archived: bool | None = None


class NotificationSummaryResponse(BaseModel):
    user_id: str
    unread_count: int
    critical_unread_count: int
    high_unread_count: int
    total_count: int
    latest_notification_at: datetime | None = None


class NotificationTestRequest(BaseModel):
    event_type: NotificationEventType
    recipient_type: NotificationRecipientType = NotificationRecipientType.USER
    recipient_id: str | None = None
    recipient_role: str | None = None
    recipient_team: str | None = None
    priority: NotificationPriority = NotificationPriority.INFO
    title: str = "Test notification"
    message: str = "This is a test notification."
    channels: list[NotificationChannel] | None = None
