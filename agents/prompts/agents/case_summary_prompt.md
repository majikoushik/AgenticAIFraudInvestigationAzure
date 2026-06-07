# Case Summary Prompt

Create an evidence-grounded fraud investigation summary using only the provided case details, risk indicators, transaction signals, customer signals, device/location signals, beneficiary signals, policy RAG results, historical case RAG results, and missing evidence.

Return JSON with:

```json
{
  "case_overview": "",
  "key_risk_indicators": [],
  "evidence_supporting_suspicion": [],
  "evidence_reducing_suspicion": [],
  "policy_references": [],
  "similar_cases": [],
  "recommended_action": "APPROVE | HOLD | ESCALATE | REJECT",
  "confidence_level": "LOW | MEDIUM | HIGH",
  "missing_evidence": [],
  "human_review_required": true,
  "rationale": "",
  "limitations": []
}
```
