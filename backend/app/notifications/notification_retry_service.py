from app.notifications.notification_config import notification_config


class NotificationRetryService:
    def should_retry(self, delivery_record: dict) -> bool:
        return delivery_record.get("status") == "FAILED" and int(delivery_record.get("attempt_count", 0)) < notification_config.max_retry_count
