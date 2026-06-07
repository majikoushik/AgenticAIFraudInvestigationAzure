# Monitoring

Azure Monitor, Application Insights, and Log Analytics assets for the fraud investigation MVP.

The KQL files target common Application Insights tables: `requests`, `dependencies`, `exceptions`, `traces`, `customEvents`, and `customMetrics`. Table names can vary depending on workspace-based Application Insights configuration.

Dashboards and alerts are placeholders that document production intent and can be adapted to enterprise Azure resource IDs.

## Alerting Assets

- `monitoring/kql/`: KQL query placeholders for API, auth, agent, RAG, LLM, guardrail, human review, and audit failure signals.
- `monitoring/alerts/`: Azure Monitor scheduled query rule placeholders.
- `docs/runbooks/`: operational response runbooks referenced by backend alert and incident records.

The local backend alert evaluator is deterministic and uses synthetic metrics and telemetry. Production deployment should connect these KQL assets to Azure Monitor action groups, Teams/email notifications, ticketing, and secure incident processes.
