# Human Override Tracking

Human override tracking records when a fraud investigator makes a final decision that differs from the AI-assisted recommendation.

## Purpose

In banking fraud investigation, AI recommendations are advisory. A human reviewer remains accountable for the final case decision. When the reviewer disagrees with the AI recommendation, the system records the override for compliance, model evaluation, operational governance, and audit review.

## Comparison Rules

- AI recommendation and human decision are normalized to `APPROVE`, `HOLD`, `ESCALATE`, or `REJECT`.
- Lowercase and legacy values such as `held`, `approved`, `escalated`, and `rejected` are normalized.
- If AI recommendation and human decision match, `human_override` is `false` and comparison status is `MATCHED`.
- If they differ, `human_override` is `true` and comparison status is `OVERRIDDEN`.
- If the AI recommendation is missing, `human_override` is `false` and comparison status is `AI_RECOMMENDATION_MISSING`.

## Override Reason

When an override occurs, the reviewer must provide an `override_reason` with at least 10 characters. The backend enforces this rule. The frontend also guides the reviewer by showing the reason field only when the selected decision differs from the AI recommendation.

## Audit Behavior

Every submitted review creates a `HUMAN_DECISION_SUBMITTED` audit event. When an override occurs, the system also creates a `HUMAN_OVERRIDE_DETECTED` audit event containing:

- case ID
- reviewer
- reviewer role
- AI recommendation
- human decision
- override reason

If the AI recommendation is missing, no override event is created. The decision audit event metadata records `override_comparison_status: AI_RECOMMENDATION_MISSING`.

## API Examples

Submit a review that overrides the AI recommendation:

```json
{
  "decision": "ESCALATE",
  "comment": "Synthetic review comment with enough detail.",
  "reviewed_by": "fraud_analyst_01",
  "reviewer_role": "FRAUD_ANALYST",
  "reason_code": "SUSPICIOUS_DEVICE",
  "evidence_acknowledged": true,
  "policy_acknowledged": true,
  "override_reason": "Beneficiary is linked to multiple suspicious synthetic cases."
}
```

Example response:

```json
{
  "case_id": "case-001",
  "decision": "ESCALATE",
  "ai_recommendation": "HOLD",
  "human_decision": "ESCALATE",
  "human_override": true,
  "override_reason": "Beneficiary is linked to multiple suspicious synthetic cases.",
  "override_comparison_status": "OVERRIDDEN",
  "message": "Human review submitted successfully"
}
```

Fetch the latest override summary:

```text
GET /api/v1/cases/{case_id}/override-summary
```

## Frontend Behavior

The case review page displays the AI recommendation in the human decision panel. If the selected human decision differs, the UI shows an override warning and requires an override reason. After submission, the case detail refreshes and displays a human override banner when an override exists.

## AI Evaluation Support

Override records help measure investigator acceptance rate, identify model blind spots, and create feedback data for future model evaluation. In a production system, these records can feed analytics dashboards and model monitoring workflows.

## Future Production Considerations

- Store audit events in immutable storage.
- Integrate reviewer identity with Microsoft Entra ID.
- Track investigator acceptance and override rates.
- Build override analytics by decision type, segment, channel, and agent version.
- Feed override outcomes into model evaluation and improvement loops.
