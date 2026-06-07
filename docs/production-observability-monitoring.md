# Production Observability and Monitoring

This MVP adds local-first, Azure Monitor-ready observability for the fraud investigation platform.

## Audit Trail vs Telemetry

Audit events are compliance records for case decisions and workflow actions. Telemetry is operational data for health, latency, failures, AI quality, RAG quality, token usage, and business KPIs. Telemetry does not replace audit.

## Architecture

Backend observability lives under `backend/app/observability/`:

- `observability_config.py`: safe environment-based configuration.
- `logging_setup.py`: JSON structured logging.
- `correlation.py`: context-local correlation IDs.
- `middleware.py`: correlation and API request telemetry.
- `telemetry_client.py`: Application Insights-ready client with local fallback.
- `pii_safe_logging.py`: recursive telemetry sanitization.
- `health_checks.py`: detailed safe health checks.
- `decorators.py`: reusable operation telemetry decorators.

Agent-side wrappers live under `agents/observability/` and emit agent, RAG, LLM, and business telemetry without requiring Azure locally.

## Local Mode

Local observability works without Azure:

```env
OBSERVABILITY_ENABLED=true
OBSERVABILITY_MODE=local
APPLICATIONINSIGHTS_CONNECTION_STRING=
LOG_FORMAT=json
TELEMETRY_LOG_PROMPTS=false
TELEMETRY_LOG_RESPONSES=false
TELEMETRY_LOG_PII=false
```

When Application Insights is not configured, sanitized telemetry is appended to `data/synthetic/telemetry_events.json`.

## Azure Monitor

Configure Application Insights through secure backend configuration:

```env
OBSERVABILITY_MODE=azure_monitor
APPLICATIONINSIGHTS_CONNECTION_STRING=<secure value>
TELEMETRY_ENVIRONMENT=prod
```

Treat the connection string as sensitive. Prefer Key Vault or pipeline secrets for deployed environments.

## Correlation IDs

`CorrelationIdMiddleware` reads `X-Correlation-ID` or generates a new ID. The response includes the same header, and telemetry/logs include the correlation ID.

## Telemetry Coverage

Application:
- API request start/completion/failure
- API latency
- 401/403 auth failure telemetry
- health check execution

Agentic AI:
- agent execution start/completion/failure
- duration
- fallback mode
- safety flag counts
- validation status

RAG and LLM:
- retrieval mode, index, result counts, empty results
- LLM latency, failures, token usage, estimated cost
- JSON parsing failures, output validation failures
- prompt injection and PII redaction events

Business:
- cases by status
- pending human review
- override rate
- AI-human match rate
- investigation/review timing
- policy citation rate

## Security Rules

Telemetry sanitization masks secrets, tokens, authorization headers, API keys, account numbers, emails, mobile values, and customer IDs. Raw prompts and raw responses are redacted by default. Chain-of-thought is never logged.

## Monitoring Assets

KQL queries, dashboard placeholders, and alert definitions live in `monitoring/`.

## Verification

```bash
cd backend
python -m pytest tests
cd ..
python -m pytest agents/tests
python -m pytest rag/tests
cd frontend
npm run build
```

## Future Improvements

- Distributed tracing across microservices
- Azure Managed Grafana
- Microsoft Sentinel integration
- SLO/SLA dashboards
- Cost dashboard
- Automated incident response
- PagerDuty or Teams notification integration
