from app.notifications.notification_dispatcher import NotificationDispatcher


class FailingChannel:
    def send(self, notification):
        del notification
        raise RuntimeError("boom")


def test_dispatcher_records_per_channel_delivery() -> None:
    result = NotificationDispatcher().dispatch({"event_type": "CASE_ASSIGNED", "priority": "INFO", "recipient_type": "ROLE", "channels": ["IN_APP", "LOCAL"]})

    assert result["status"] == "SENT"
    assert len(result["delivery_records"]) == 2


def test_dispatcher_failure_does_not_raise() -> None:
    dispatcher = NotificationDispatcher()
    dispatcher.channels["LOCAL"] = FailingChannel()

    result = dispatcher.dispatch({"event_type": "CASE_ASSIGNED", "priority": "INFO", "recipient_type": "ROLE", "channels": ["LOCAL"]})

    assert result["status"] == "FAILED"
