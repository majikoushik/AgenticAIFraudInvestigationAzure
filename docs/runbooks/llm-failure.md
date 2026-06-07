# LLM Failure

## Alert meaning
LLM calls are failing above the expected threshold.

## Severity
SEV1_HIGH.

## Possible causes
Invalid endpoint or deployment, quota exhaustion, authentication failure, provider outage, JSON parsing issues, or prompt validation failure.

## Immediate triage steps
Check provider configuration, deployment availability, request failures, and fallback behavior.

## KQL queries to run
Run `monitoring/kql/high-llm-failure-rate.kql`.

## Application logs to check
Inspect `LLM_CALL_FAILED`, `LLM_JSON_PARSE_FAILED`, `LLM_OUTPUT_VALIDATION_FAILED`, and `AGENT_FALLBACK_USED`.

## Azure resources to inspect
Azure OpenAI deployment, Key Vault references, Container Apps environment variables, and Application Insights.

## Safe mitigation steps
Switch to local mode, reduce request volume, rotate only validated configuration, or rollback provider integration changes.

## Escalation path
AI platform team, then Azure support if service health confirms an outage.

## When to resolve
Resolve after LLM calls succeed and fallback usage returns to normal.

## Post-incident review notes
Document failure mode, affected case IDs, and fallback effectiveness.
