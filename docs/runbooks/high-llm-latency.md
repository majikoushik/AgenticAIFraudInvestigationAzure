# High LLM Latency

## Alert meaning
LLM provider calls are slower than the configured threshold.

## Severity
SEV2_MEDIUM.

## Possible causes
Provider capacity, deployment throttling, prompt size growth, retry behavior, or network latency.

## Immediate triage steps
Check LLM latency by deployment, prompt size, token count, and request volume.

## KQL queries to run
Run `monitoring/kql/high-llm-latency.kql`.

## Application logs to check
Inspect `LLM_CALL_STARTED`, `LLM_CALL_COMPLETED`, and `LLM_TOKEN_USAGE_RECORDED`.

## Azure resources to inspect
Azure OpenAI deployment, regional availability, quotas, and backend Container App.

## Safe mitigation steps
Enable local deterministic fallback, reduce prompt context, lower max tokens, or use a healthy deployment.

## Escalation path
AI platform owner and Azure support contact if provider outage is suspected.

## When to resolve
Resolve after average and p95 LLM latency return below threshold.

## Post-incident review notes
Record deployment, model, prompt size, and fallback usage.
