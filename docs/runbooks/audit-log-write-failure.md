# Audit Log Write Failure

## Alert meaning
The system failed to write an audit event.

## Severity
SEV0_CRITICAL.

## Possible causes
File permission issue, storage outage, malformed audit payload, disk exhaustion, or repository write regression.

## Immediate triage steps
Stop risky state-changing operations if auditability is impaired and preserve available logs.

## KQL queries to run
Run `monitoring/kql/audit-log-write-failure.kql`.

## Application logs to check
Inspect audit service errors, `AUDIT_LOG_WRITE_FAILURE`, decision submissions, incident changes, and filesystem errors.

## Azure resources to inspect
Storage account or mounted volume, Container Apps revision, Application Insights, and Key Vault references.

## Safe mitigation steps
Switch to backup audit sink, restore write permissions, reduce noncritical operations, and do not bypass audit logging.

## Escalation path
Security/compliance owner and platform on-call.

## When to resolve
Resolve after audit writes are confirmed and any missing events are reconstructed from reliable logs.

## Post-incident review notes
Record missing event window, reconstruction method, and compliance follow-up.
