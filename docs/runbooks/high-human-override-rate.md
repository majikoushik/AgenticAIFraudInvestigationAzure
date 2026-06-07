# High Human Override Rate

## Alert meaning
Investigators are overriding AI recommendations above the configured threshold.

## Severity
SEV1_HIGH.

## Possible causes
Model drift, weak evidence summaries, missing policy citations, new fraud pattern, or workflow mismatch.

## Immediate triage steps
Review overridden cases, compare AI recommendations with human decisions, and identify common disagreement reasons.

## KQL queries to run
Run `monitoring/kql/high-human-override-rate.kql`.

## Application logs to check
Inspect `HUMAN_OVERRIDE_DETECTED`, `HUMAN_DECISION_SUBMITTED`, and investigation summaries.

## Azure resources to inspect
Application Insights, backend case data, Azure OpenAI deployment, and Azure AI Search index.

## Safe mitigation steps
Raise confidence thresholds, require manual policy review, switch to advisory-only summaries, or tune prompts/retrieval.

## Escalation path
Fraud operations lead and AI governance owner.

## When to resolve
Resolve after override rate returns below threshold and sample disagreements are explained.

## Post-incident review notes
Record override themes, model gaps, and policy updates.
