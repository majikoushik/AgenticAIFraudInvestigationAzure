# Case Assignment and Investigator Queue

## Purpose

The assignment MVP adds case ownership and queue management to the local synthetic fraud investigation workflow. It lets managers assign or reassign cases, investigators accept or release their own cases, and managers or auditors monitor team workload and SLA risk.

## Assignment Lifecycle

Cases use these assignment states:

- `UNASSIGNED`: available for manager assignment or analyst self-assignment when enabled.
- `ASSIGNED`: owned by an investigator but not yet accepted.
- `ACCEPTED`: investigator has accepted active ownership.
- `RELEASED`: returned to the unassigned queue.
- `TRANSFERRED`: moved to another investigator or specialist team.

Closed cases cannot be assigned, accepted, released, or transferred.

## Queue Types

- My Queue: cases assigned to the current authenticated user.
- Unassigned Queue: cases without an owner.
- Team Queue: team-wide queue for managers, compliance, auditors, and admins.
- SLA Risk Queue: cases with `AT_RISK` or `BREACHED` SLA status.
- Workload: active case counts, priority distribution, SLA status, and overloaded investigator indicators.

## Role Permissions

- `FRAUD_ANALYST`: view own queue, accept cases, release own cases, view own assignment history.
- `FRAUD_MANAGER`: assign, reassign, accept, release, transfer, view all queues, view history, refresh SLA.
- `COMPLIANCE_OFFICER`: view own queue and team queue, accept/release own compliance cases, view history.
- `AUDITOR`: view team queue and history only.
- `ADMIN`: full access.

Backend permissions are authoritative. Frontend role checks only hide invalid actions for usability.

## API Examples

Assign a case:

```http
POST /api/v1/cases/case-001/assign
X-Demo-User: fraud_manager_01
X-Demo-Role: FRAUD_MANAGER
Content-Type: application/json
```

```json
{
  "assigned_to": "fraud_analyst_01",
  "assigned_to_name": "Fraud Analyst 01",
  "assigned_to_role": "FRAUD_ANALYST",
  "assigned_team": "Fraud Operations",
  "assignment_priority": "HIGH",
  "comment": "High-value new beneficiary case."
}
```

Queue endpoints:

- `GET /api/v1/queues/my`
- `GET /api/v1/queues/unassigned`
- `GET /api/v1/queues/team?team=Fraud%20Operations`
- `GET /api/v1/queues/escalated`
- `GET /api/v1/queues/sla-risk`
- `GET /api/v1/assignment/workload`
- `GET /api/v1/cases/{case_id}/assignment-history`
- `POST /api/v1/assignment/sla/refresh`

## SLA Calculation

Default due dates are set on assignment when `AUTO_SET_SLA_ON_ASSIGNMENT=true`.

- `LOW`: 72 hours
- `MEDIUM`: 48 hours
- `HIGH`: 24 hours
- `CRITICAL`: 4 hours

SLA status is:

- `NOT_APPLICABLE`: no due date.
- `BREACHED`: current UTC time is after `sla_due_at`.
- `AT_RISK`: due within 2 hours.
- `ON_TRACK`: due date exists and is not at risk.

## Workload Metrics

Workload is calculated from local JSON cases and `data/synthetic/investigators.json`.

Metrics include total assigned/unassigned cases, cases by investigator, cases by priority, cases by SLA status, overloaded investigators, available investigators, and average cases per investigator.

## Audit Behavior

Assignment actions write:

- Assignment history to `data/synthetic/assignment_history.json`.
- Audit events to `data/synthetic/audit_events.json`.
- Local telemetry events when observability is enabled.

History records contain assignment metadata and truncated comments only. They do not store case evidence or sensitive details.

## Frontend Pages

- `/queues/my`
- `/queues/unassigned`
- `/queues/team`
- `/queues/sla-risk`
- `/assignment/workload`
- `/cases/[caseId]` includes assignment summary, assignment actions, and assignment history.

## Local Storage

The MVP uses local JSON files:

- `data/synthetic/fraud_alerts.json`
- `data/synthetic/assignment_history.json`
- `data/synthetic/investigators.json`

This is intentionally isolated behind repository and service classes so it can later move to Cosmos DB or Azure SQL.

## Future Production Improvements

- Cosmos DB or Azure SQL assignment table.
- Entra ID user directory integration.
- Teams notification on assignment.
- Automatic workload-based assignment.
- Skill-based routing.
- Supervisor approval for transfer.
- SLA breach alerts.
- Power BI workload dashboard.
