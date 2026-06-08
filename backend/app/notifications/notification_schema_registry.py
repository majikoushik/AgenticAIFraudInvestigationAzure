from app.core.constants import NotificationChannel, NotificationEventType, NotificationPriority, NotificationRecipientType, NotificationStatus


NOTIFICATION_ENUM_REGISTRY = {
    "event_types": [item.value for item in NotificationEventType],
    "priorities": [item.value for item in NotificationPriority],
    "channels": [item.value for item in NotificationChannel],
    "statuses": [item.value for item in NotificationStatus],
    "recipient_types": [item.value for item in NotificationRecipientType],
}
