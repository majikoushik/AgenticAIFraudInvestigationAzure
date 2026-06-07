# Agent Timeout

## Alert meaning
Agent execution duration exceeded the configured timeout.

## Severity
SEV2_MEDIUM.

## Possible causes
Large prompts, slow retrieval, slow provider calls, retry loops, or resource saturation.

## Immediate triage steps
Check which agent timed out and compare RAG, LLM, and orchestration timings.

## KQL queries to run
Run `monitoring/kql/agent-timeout.kql`.

## Application logs to check
Inspect `AGENT_EXECUTION_STARTED`, `AGENT_EXECUTION_COMPLETED`, `LLM_CALL_COMPLETED`, and `RAG_RETRIEVAL_COMPLETED`.

## Azure resources to inspect
Container Apps CPU/memory, Azure OpenAI latency, Azure AI Search latency, and Application Insights traces.

## Safe mitigation steps
Reduce context size, lower top-k retrieval, enable local fallback, or scale backend replicas.

## Escalation path
AI platform team and platform on-call.

## When to resolve
Resolve after execution durations remain below timeout for the affected agents.

## Post-incident review notes
Capture timeout source, case shape, and context reduction work.
