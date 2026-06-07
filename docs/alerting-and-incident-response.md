# Alerting And Incident Response

This MVP adds a local alerting and incident response layer for operational, AI, RAG, security, cost, and human-review signals. It is deterministic and does not call external notification or monitoring APIs by default.

## Local Stores

- `data/synthetic/alerts.json`: active and resolved alert events.
- `data/synthetic/incidents.json`: incidents created from alerts.
- `data/synthetic/notifications.json`: local notification records when notifications are enabled.
- `data/synthetic/telemetry_events.json`: local sanitized telemetry used by the evaluator.

All stores contain synthetic operational data only.

## Admin APIs

Alert endpoints require the `ADMIN_CONFIG` permission:

- `GET /api/v1/alerts`
- `GET /api/v1/alerts/{alert_id}`
- `POST /api/v1/alerts/evaluate`
- `POST /api/v1/alerts/simulate`
- `POST /api/v1/alerts/{alert_id}/resolve`

Incident endpoints also require `ADMIN_CONFIG`:

- `GET /api/v1/incidents`
- `GET /api/v1/incidents/{incident_id}`
- `PATCH /api/v1/incidents/{incident_id}/status`
- `PATCH /api/v1/incidents/{incident_id}/assign`
- `POST /api/v1/incidents/{incident_id}/timeline`
- `POST /api/v1/incidents/{incident_id}/close`

Use local demo headers in development:

```text
X-Demo-User=admin_user
X-Demo-Role=ADMIN
```

## Alert Evaluation

`POST /api/v1/alerts/evaluate` evaluates local metrics and telemetry for key rules including API error rate, API latency, agent failures, RAG empty results, citation failures, LLM latency, token usage, prompt injection, guardrail violations, human override rate, stuck review cases, and low policy citation accuracy.

SEV0 and SEV1 alerts create incidents automatically when `INCIDENT_AUTO_CREATE_ENABLED=true`.

## Simulation

`POST /api/v1/alerts/simulate` creates a deterministic alert for local demos and tests. High-severity simulations create a linked incident.

Example:

```json
{
  "alert_type": "HIGH_API_ERROR_RATE",
  "severity": "SEV1_HIGH",
  "title": "Simulated API error alert",
  "description": "Synthetic alert for local incident response testing."
}
```

## Runbooks

Runbooks live under `docs/runbooks/`. Each runbook includes alert meaning, severity, causes, triage, KQL, logs, Azure resources, mitigation, escalation, resolution criteria, and post-incident notes.

## Azure Placeholders

The Bicep structure includes placeholders for action groups and monitor alert rules. KQL files live in `monitoring/kql/`, and alert rule JSON placeholders live in `monitoring/alerts/`.

Production delivery should wire these assets to Azure Monitor, Application Insights, Log Analytics, Teams, email, and ticketing systems through secure configuration.
