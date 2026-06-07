# Guardrail Violation

## Alert meaning
An AI safety guardrail rejected or flagged system output.

## Severity
SEV1_HIGH.

## Possible causes
Unsupported recommendation, missing human review, unsafe accusation language, unvalidated citation, or policy mismatch.

## Immediate triage steps
Review the flagged output, evidence package, and reviewer validation result.

## KQL queries to run
Run `monitoring/kql/guardrail-violation-detected.kql`.

## Application logs to check
Inspect `GUARDRAIL_VIOLATION_DETECTED`, `LLM_OUTPUT_VALIDATION_FAILED`, and `AGENT_OUTPUT_VALIDATION_FAILED`.

## Azure resources to inspect
Backend Container App, Azure OpenAI deployment, Application Insights, and prompt configuration.

## Safe mitigation steps
Block automated recommendation display, require human-only review, and rollback prompt or validator changes.

## Escalation path
AI governance owner and fraud operations lead.

## When to resolve
Resolve after the output path passes guardrails with representative test cases.

## Post-incident review notes
Document failed guardrail, user impact, and validation improvement.
