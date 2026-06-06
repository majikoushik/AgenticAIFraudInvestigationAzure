# Case Status Lifecycle

## Purpose

The case status lifecycle keeps fraud investigation cases moving through a backend-enforced state machine. It prevents invalid state changes, records audit events for every transition, and keeps AI investigation and human review workflows consistent.

## Status Definitions

- `NEW`: Case is created and ready for AI investigation.
- `AI_INVESTIGATION_IN_PROGRESS`: Local or Azure-ready agent workflow is running.
- `AI_INVESTIGATION_COMPLETED`: AI investigation package has been generated.
- `PENDING_HUMAN_REVIEW`: Case is ready for investigator or manager review.
- `APPROVED`: Human reviewer approved the case outcome.
- `HELD`: Human reviewer placed the case on hold.
- `ESCALATED`: Human reviewer escalated the case.
- `REJECTED`: Human reviewer rejected the case outcome.
- `CLOSED`: Terminal state. No further transitions are allowed.

## Allowed Transitions

| Current status | Allowed next status |
| --- | --- |
| `NEW` | `AI_INVESTIGATION_IN_PROGRESS` |
| `AI_INVESTIGATION_IN_PROGRESS` | `AI_INVESTIGATION_COMPLETED` |
| `AI_INVESTIGATION_COMPLETED` | `PENDING_HUMAN_REVIEW` |
| `PENDING_HUMAN_REVIEW` | `APPROVED`, `HELD`, `ESCALATED`, `REJECTED` |
| `APPROVED` | `CLOSED` |
| `HELD` | `CLOSED` |
| `ESCALATED` | `CLOSED` |
| `REJECTED` | `CLOSED` |
| `CLOSED` | None |

## AI Investigation

`POST /api/v1/cases/{case_id}/investigate` is allowed only from `NEW`.

Successful investigation transitions:

1. `NEW` -> `AI_INVESTIGATION_IN_PROGRESS`
2. `AI_INVESTIGATION_IN_PROGRESS` -> `AI_INVESTIGATION_COMPLETED`
3. `AI_INVESTIGATION_COMPLETED` -> `PENDING_HUMAN_REVIEW`

Each transition writes an audit event.

## Human Review

Human review decisions use `CaseStatusService`:

- `APPROVE` -> `APPROVED`
- `HOLD` -> `HELD`
- `ESCALATE` -> `ESCALATED`
- `REJECT` -> `REJECTED`

Reviews can be submitted only from `PENDING_HUMAN_REVIEW`.

## Audit Events

Status changes append events to `data/synthetic/audit_events.json` for the MVP. Events are returned in timestamp order by:

```http
GET /api/v1/cases/{case_id}/audit
```

## API Examples

Get status:

```http
GET /api/v1/cases/case-001/status
```

Patch status:

```json
{
  "target_status": "HELD",
  "actor": "fraud_analyst_01",
  "actor_role": "FRAUD_ANALYST",
  "comment": "Case held for customer confirmation"
}
```

Response:

```json
{
  "case_id": "case-001",
  "previous_status": "PENDING_HUMAN_REVIEW",
  "new_status": "HELD",
  "allowed_next_statuses": ["CLOSED"],
  "message": "Case status updated successfully"
}
```

## Future Production Considerations

- Persist cases and audit events in Cosmos DB instead of local JSON.
- Derive actor and role from Azure Entra ID claims.
- Enforce role-based transition permissions with backend authorization policies.
- Emit audit events to Application Insights, Event Grid, or Service Bus for downstream governance workflows.
