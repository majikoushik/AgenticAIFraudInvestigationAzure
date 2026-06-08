# Notification Failures Runbook

## Purpose

Investigate high notification delivery failure rates without exposing SMTP credentials, webhook URLs, tokens, prompts, responses, or PII.

## Triage Steps

1. Open the admin notification health page at `/admin/notifications`.
2. Confirm local stores are writable and enabled channels match expected configuration.
3. Review recent failed delivery records in `data/synthetic/notifications.json` for sanitized `error_message` values.
4. Check Application Insights or local telemetry for `NOTIFICATION_DISPATCH_FAILED` and `NOTIFICATION_CHANNEL_SKIPPED`.
5. Verify external channel configuration through Key Vault or secure app settings, not source files.

## Common Causes

- Email, Teams, or webhook channel enabled without production credentials.
- Network restriction to SMTP or webhook endpoints.
- Payload rejected by downstream system.
- Local JSON store is not writable.

## Recovery

- Disable failing external channels until credentials and network paths are fixed.
- Keep `IN_APP` and `LOCAL` enabled for operational continuity.
- Re-send critical notifications manually if needed.

## Production Improvements

- Move delivery to Service Bus.
- Use Durable Functions for retry.
- Use Azure Communication Services or Microsoft Graph for email.
- Use Teams adaptive cards with secrets in Key Vault.
