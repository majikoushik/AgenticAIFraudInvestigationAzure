# High API Error Rate

## Alert meaning
API 5xx responses are above the configured threshold.

## Severity
SEV1_HIGH.

## Possible causes
Backend regression, failed deployment, dependency outage, exhausted compute, or malformed request handling.

## Immediate triage steps
Check affected routes, recent deployments, container health, and dependency failures.

## KQL queries to run
Run `monitoring/kql/high-api-error-rate.kql`.

## Application logs to check
Inspect `API_REQUEST_COMPLETED`, `API_REQUEST_FAILED`, exception logs, and correlation IDs.

## Azure resources to inspect
Container Apps, Application Insights, Log Analytics, Azure AI Search, and Azure OpenAI dependencies.

## Safe mitigation steps
Rollback the latest deployment, scale the backend, disable unhealthy optional integrations, or route traffic to fallback mode.

## Escalation path
Platform on-call, then security if failures affect fraud review integrity.

## When to resolve
Resolve after the error rate remains below threshold for at least one monitoring window.

## Post-incident review notes
Record root cause, affected endpoints, customer impact, and prevention work.
