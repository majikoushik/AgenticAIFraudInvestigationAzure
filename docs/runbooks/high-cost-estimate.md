# High Cost Estimate

## Alert meaning
Estimated LLM or AI service cost exceeded the configured threshold.

## Severity
SEV2_MEDIUM.

## Possible causes
Token spike, traffic spike, retry storm, wrong model deployment, or expanded context windows.

## Immediate triage steps
Compare cost estimate by route, model, token usage, and request source.

## KQL queries to run
Run `monitoring/kql/high-cost-estimate.kql`.

## Application logs to check
Inspect `LLM_COST_ESTIMATED`, `LLM_TOKEN_USAGE_RECORDED`, and `API_REQUEST_COMPLETED`.

## Azure resources to inspect
Azure OpenAI usage metrics, Application Insights, cost management, and backend scaling configuration.

## Safe mitigation steps
Reduce model usage, enforce token caps, disable noncritical simulations, or switch to local deterministic mode.

## Escalation path
AI platform owner and engineering finance owner.

## When to resolve
Resolve after cost estimates are below threshold and runaway traffic is stopped.

## Post-incident review notes
Capture spend estimate, driver, and cost guardrail improvements.
