# Human Review Workflow

## Overview

The MVP uses a human-in-the-loop workflow for final fraud case actions. AI agents can recommend actions, summarize evidence, and flag risk, but a human reviewer must submit the final case decision.

## Status Lifecycle

Allowed transitions:

- `NEW` -> `AI_INVESTIGATION_IN_PROGRESS`
- `AI_INVESTIGATION_IN_PROGRESS` -> `AI_INVESTIGATION_COMPLETED`
- `AI_INVESTIGATION_COMPLETED` -> `PENDING_HUMAN_REVIEW`
- `PENDING_HUMAN_REVIEW` -> `APPROVED`
- `PENDING_HUMAN_REVIEW` -> `HELD`
- `PENDING_HUMAN_REVIEW` -> `ESCALATED`
- `PENDING_HUMAN_REVIEW` -> `REJECTED`
- `APPROVED` -> `CLOSED`
- `HELD` -> `CLOSED`
- `ESCALATED` -> `CLOSED`
- `REJECTED` -> `CLOSED`

Invalid transitions return HTTP 400.

## Roles And Actions

- `FRAUD_ANALYST`: `HOLD`, `ESCALATE`, `REJECT`
- `FRAUD_MANAGER`: `APPROVE`, `HOLD`, `ESCALATE`, `REJECT`
- `COMPLIANCE_OFFICER`: `ESCALATE`, `HOLD`
- `AUDITOR`: view only

Case closure is limited to `FRAUD_MANAGER` and `COMPLIANCE_OFFICER`.

## Review Submission Rules

A review can be submitted only when the case is `PENDING_HUMAN_REVIEW`.

Required fields:

- Decision
- Reviewer name
- Reviewer role
- Reason code
- Comment with at least 10 characters
- Evidence acknowledgement
- Policy acknowledgement

If the human decision differs from the AI recommendation, `override_reason` is required.

## Audit Events

The backend records structured audit events for:

- `CASE_STATUS_CHANGED`
- `AI_INVESTIGATION_STARTED`
- `AI_INVESTIGATION_COMPLETED`
- `HUMAN_DECISION_SUBMITTED`
- `HUMAN_OVERRIDE_DETECTED`
- `CASE_CLOSED`

Audit data is stored in memory for the MVP and shaped for future Cosmos DB persistence.

## Human Override Tracking

The service compares the AI recommendation with the submitted human decision.

Example:

```json
{
  "ai_recommendation": "HOLD",
  "human_decision": "ESCALATE",
  "human_override": true,
  "override_reason": "Beneficiary linked to multiple suspicious synthetic cases"
}
```

## Future Azure Entra ID Integration

Current role values are submitted by the frontend for MVP testing. In production, reviewer identity and role should be derived from Azure Entra ID claims, not trusted from request payloads.
