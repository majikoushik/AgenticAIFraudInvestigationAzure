# Monitoring

Azure Monitor, Application Insights, and Log Analytics assets for the fraud investigation MVP.

The KQL files target common Application Insights tables: `requests`, `dependencies`, `exceptions`, `traces`, `customEvents`, and `customMetrics`. Table names can vary depending on workspace-based Application Insights configuration.

Dashboards and alerts are placeholders that document production intent and can be adapted to enterprise Azure resource IDs.

## Alerting Assets

- `monitoring/kql/`: KQL query placeholders for API, auth, agent, RAG, LLM, guardrail, human review, and audit failure signals.
- `monitoring/alerts/`: Azure Monitor scheduled query rule placeholders.
- `docs/runbooks/`: operational response runbooks referenced by backend alert and incident records.

The local backend alert evaluator is deterministic and uses synthetic metrics and telemetry. Production deployment should connect these KQL assets to Azure Monitor action groups, Teams/email notifications, ticketing, and secure incident processes.

## Cost Monitoring

Cost monitoring uses local token and estimated cost records for the MVP. Production monitoring should add Azure Cost Management, budget alerts, and dashboards that reconcile local estimates with official Azure billing data.
## Notification Monitoring

- `kql/notification-failures.kql`: placeholder KQL for failed notification dispatches.
- `alerts/notification-failure-rate-high.json`: disabled alert rule placeholder for production wiring.
- Runbook: `docs/runbooks/notification-failures.md`.

Production notification secrets such as SMTP passwords and webhook URLs must come from Key Vault or secure app settings, never from monitoring files.
# AI Feedback Alerts

Feedback alert placeholders cover high negative feedback rate, critical AI feedback, wrong citation feedback, and incorrect recommendation feedback. The KQL files are local scaffolds for future Azure Monitor alert rules.
