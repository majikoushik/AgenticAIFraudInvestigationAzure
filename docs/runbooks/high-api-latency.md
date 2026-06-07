# High API Latency

## Alert meaning
Average API request latency is above the configured threshold.

## Severity
SEV2_MEDIUM.

## Possible causes
Cold starts, high traffic, slow RAG retrieval, slow LLM provider calls, or backend resource saturation.

## Immediate triage steps
Compare latency by route, check dependency timings, and identify whether agent investigation routes are affected.

## KQL queries to run
Run `monitoring/kql/high-api-latency.kql`.

## Application logs to check
Inspect `API_REQUEST_COMPLETED`, `AGENT_EXECUTION_COMPLETED`, `RAG_RETRIEVAL_COMPLETED`, and `LLM_CALL_COMPLETED`.

## Azure resources to inspect
Container Apps replicas, Application Insights dependency traces, Azure AI Search, and Azure OpenAI deployments.

## Safe mitigation steps
Scale the backend, reduce investigation context size, enable local fallback, or pause noncritical background evaluations.

## Escalation path
Platform on-call, then AI platform team if LLM or RAG latency dominates.

## When to resolve
Resolve after latency stays below threshold and investigation endpoints are responsive.

## Post-incident review notes
Capture p95 latency, bottleneck component, and tuning actions.
