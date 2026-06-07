# Agent Failure

## Alert meaning
Agent executions are failing above the configured threshold.

## Severity
SEV1_HIGH.

## Possible causes
Malformed case payloads, code regression, provider integration issue, prompt validation failure, or missing RAG context.

## Immediate triage steps
Identify failing agent names, compare failures by case type, and verify whether local deterministic fallback works.

## KQL queries to run
Run `monitoring/kql/high-agent-failure-rate.kql`.

## Application logs to check
Inspect `AGENT_EXECUTION_FAILED`, `AGENT_OUTPUT_VALIDATION_FAILED`, and investigation correlation IDs.

## Azure resources to inspect
Backend Container App, Application Insights, Azure OpenAI deployment, Azure AI Search index, and Key Vault references.

## Safe mitigation steps
Switch to local mode, disable the affected provider path, rollback recent agent changes, or require manual investigation only.

## Escalation path
AI platform team, then fraud operations if decisions are delayed.

## When to resolve
Resolve after agent failures stay below threshold and sample investigations complete successfully.

## Post-incident review notes
Document failing agents, impacted cases, and validation gaps.
