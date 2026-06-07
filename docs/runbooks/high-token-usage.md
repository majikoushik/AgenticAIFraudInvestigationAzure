# High Token Usage

## Alert meaning
LLM token usage exceeded the configured threshold.

## Severity
SEV2_MEDIUM.

## Possible causes
Large RAG context, repeated retries, verbose prompts, increased case volume, or missing truncation.

## Immediate triage steps
Check token usage by route, agent, and model deployment.

## KQL queries to run
Run `monitoring/kql/high-token-usage.kql`.

## Application logs to check
Inspect `LLM_TOKEN_USAGE_RECORDED`, `LLM_CALL_COMPLETED`, and `AGENT_EXECUTION_COMPLETED`.

## Azure resources to inspect
Azure OpenAI usage, Container Apps logs, and Application Insights custom metrics.

## Safe mitigation steps
Reduce top-k retrieval, trim prompts, lower max output tokens, or temporarily disable expensive evaluation paths.

## Escalation path
AI platform owner and finance owner if cost exposure is material.

## When to resolve
Resolve after token usage remains below threshold for one monitoring window.

## Post-incident review notes
Record usage driver, estimated cost, and prompt or retrieval changes.
