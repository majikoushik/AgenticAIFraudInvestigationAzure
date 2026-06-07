# Stuck Pending Review Cases

## Alert meaning
Fraud cases have remained in `PENDING_HUMAN_REVIEW` beyond the allowed time.

## Severity
SEV1_HIGH.

## Possible causes
Reviewer queue backlog, failed assignment, notification issue, unavailable investigator, or workflow status bug.

## Immediate triage steps
List stuck cases, assign owners, verify notifications, and check whether decision endpoints are working.

## KQL queries to run
Run `monitoring/kql/stuck-pending-review-cases.kql`.

## Application logs to check
Inspect `CASE_STUCK_IN_REVIEW`, `CASE_STATUS_CHANGED`, `NOTIFICATION_SENT`, and `NOTIFICATION_FAILED`.

## Azure resources to inspect
Backend Container App, Application Insights, notification integration, and fraud operations queue.

## Safe mitigation steps
Manually assign cases, notify reviewers through backup channel, and keep human review requirement intact.

## Escalation path
Fraud operations lead, then platform on-call if workflow APIs are failing.

## When to resolve
Resolve after stuck cases are reviewed or reassigned and new cases move through the queue normally.

## Post-incident review notes
Document queue age, staffing impact, and workflow fix.
