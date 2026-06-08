from app.notifications.notification_renderer import NotificationRenderer
from app.notifications.notification_template_repository import NotificationTemplateRepository


def test_notification_template_renders_safe_message(tmp_path) -> None:
    path = tmp_path / "templates.json"
    path.write_text('[{"template_id":"T1","event_type":"CASE_ASSIGNED","title_template":"Case {{case_id}}","message_template":"Assigned to {{assigned_to_name}}","default_priority":"HIGH","default_channels":["IN_APP"],"enabled":true}]', encoding="utf-8")

    rendered = NotificationRenderer(NotificationTemplateRepository(path)).render("CASE_ASSIGNED", {"case_id": "case-1", "assigned_to_name": "Analyst"})

    assert rendered["title"] == "Case case-1"
    assert rendered["message"] == "Assigned to Analyst"


def test_missing_template_falls_back_safely(tmp_path) -> None:
    rendered = NotificationRenderer(NotificationTemplateRepository(tmp_path / "templates.json")).render("UNKNOWN_EVENT", {"message": "hello"})

    assert rendered["title"] == "Unknown Event"
    assert rendered["message"] == "hello"
