from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_test_notification_endpoint_works_in_local_mode() -> None:
    response = client.post(
        "/api/v1/notifications/test",
        headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"},
        json={
            "event_type": "CASE_ASSIGNED",
            "recipient_type": "USER",
            "recipient_id": "fraud_analyst_01",
            "priority": "INFO",
            "title": "Test notification",
            "message": "This is a test notification."
        },
    )

    assert response.status_code == 200
    assert response.json()["recipient_id"] == "fraud_analyst_01"


def test_user_can_list_own_notifications_and_mark_read_archive() -> None:
    create = client.post(
        "/api/v1/notifications/test",
        headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"},
        json={"event_type": "CASE_ASSIGNED", "recipient_type": "USER", "recipient_id": "fraud_analyst_01", "title": "Route test", "message": "Route test."},
    )
    notification_id = create.json()["notification_id"]

    list_response = client.get("/api/v1/notifications/me", headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"})
    read_response = client.post(f"/api/v1/notifications/{notification_id}/read", headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"})
    archive_response = client.post(f"/api/v1/notifications/{notification_id}/archive", headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"})

    assert list_response.status_code == 200
    assert read_response.status_code == 200
    assert archive_response.status_code == 200


def test_user_cannot_read_another_users_private_notification() -> None:
    create = client.post(
        "/api/v1/notifications/test",
        headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"},
        json={"event_type": "CASE_ASSIGNED", "recipient_type": "USER", "recipient_id": "fraud_analyst_01", "title": "Private", "message": "Private."},
    )

    response = client.get(f"/api/v1/notifications/{create.json()['notification_id']}", headers={"X-Demo-User": "fraud_analyst_02", "X-Demo-Role": "FRAUD_ANALYST"})

    assert response.status_code == 403


def test_mark_all_read_and_preferences_work() -> None:
    prefs = client.patch(
        "/api/v1/notifications/preferences/me",
        headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"},
        json={"enabled": True, "channels": ["IN_APP", "LOCAL"]},
    )
    read_all = client.post("/api/v1/notifications/read-all", headers={"X-Demo-User": "fraud_analyst_01", "X-Demo-Role": "FRAUD_ANALYST"})

    assert prefs.status_code == 200
    assert read_all.status_code == 200


def test_admin_can_list_notifications_and_health() -> None:
    list_response = client.get("/api/v1/admin/notifications", headers={"X-Demo-User": "admin_01", "X-Demo-Role": "ADMIN"})
    health_response = client.get("/api/v1/admin/notifications/health", headers={"X-Demo-User": "admin_01", "X-Demo-Role": "ADMIN"})

    assert list_response.status_code == 200
    assert health_response.status_code == 200
    assert health_response.json()["secret_values_redacted"] is True
