# Notification System

## Purpose

The notification system provides local-first, production-ready notification structure for fraud investigation workflows. It supports in-app notifications, local delivery history, preferences, templates, retry metadata, and safe placeholders for email, Microsoft Teams, and generic webhooks.

## Event Types

Supported events include assignment, case lifecycle, human review, SLA, alert and incident, cost, safety, health, and admin configuration notifications. The centralized enum is `NotificationEventType` in `backend/app/core/constants.py`.

## Channels

- `IN_APP`: persisted inbox notifications for the frontend.
- `LOCAL`: local delivery record for development.
- `EMAIL`: placeholder that skips unless SMTP is configured.
- `TEAMS`: placeholder that skips unless a Teams webhook is configured.
- `WEBHOOK`: placeholder that skips unless a generic webhook URL is configured.

External channels do not require credentials for tests.

## Preferences

Preferences are stored in `data/synthetic/notification_preferences.json`. Users can enable or disable notifications, choose channels, and store quiet-hour metadata. Critical security and budget notifications are not fully suppressible in the backend service.

## Templates

Templates are stored in `data/synthetic/notification_templates.json`. Rendering uses simple `{{placeholder}}` replacement only. No arbitrary code is evaluated.

## Delivery Status and Retry

Each notification stores delivery records by channel with status, attempt count, timestamp, and sanitized error text. Retry support is structured through `NotificationRetryService`; production async retry can later move to Service Bus and Durable Functions.

## Audit and Observability

Notification creation, send/failure, read/archive, preference updates, and test sends emit audit events. Dispatch emits telemetry events without secrets, raw prompts, raw responses, JWT tokens, webhook URLs, SMTP passwords, or PII-heavy payloads.

## Frontend

The frontend includes:

- Header notification bell with unread count.
- `/notifications` inbox.
- `/notifications/preferences` preference page.
- `/admin/notifications` safe health and test panel.

## API Examples

Send a local test notification:

```http
POST /api/v1/notifications/test
X-Demo-User: admin_01
X-Demo-Role: ADMIN
Content-Type: application/json
```

```json
{
  "event_type": "CASE_ASSIGNED",
  "recipient_type": "USER",
  "recipient_id": "fraud_analyst_01",
  "priority": "INFO",
  "title": "Test notification",
  "message": "This is a test notification."
}
```

Read inbox:

```http
GET /api/v1/notifications/me?unread_only=true
```

Admin health:

```http
GET /api/v1/admin/notifications/health
```

## Security and Privacy

- Do not commit SMTP credentials or webhook URLs.
- Do not log secrets, JWTs, API keys, raw prompts, raw model responses, or PII-heavy content.
- Notification metadata is sanitized before storage.
- Users can access only their user notifications plus matching role/team notifications.
- Admins can view all notifications.
- Notification failures do not break primary fraud workflows.

## Local Testing

1. Start backend and frontend.
2. Log in as `FRAUD_ANALYST`.
3. Open `/notifications`.
4. Log in as `ADMIN` or local demo mode and open `/admin/notifications`.
5. Send a test notification to `fraud_analyst_01`.
6. Return to the analyst inbox and mark the notification read or archive it.

## Future Production Improvements

- Azure Communication Services email.
- Microsoft Graph email.
- Teams adaptive cards.
- Azure Event Grid.
- Service Bus async dispatch.
- Durable Functions retry.
- Notification digest emails.
- Escalation notifications.
- Mobile push notifications.
- Entra ID user directory integration.
