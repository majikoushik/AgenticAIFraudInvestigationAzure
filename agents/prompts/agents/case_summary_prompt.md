Generate a structured fraud investigation summary using only the provided case evidence.

Return JSON with:
- case_overview
- key_risk_indicators
- evidence_supporting_suspicion
- evidence_reducing_suspicion
- policy_references
- similar_cases
- recommended_action
- confidence_level
- missing_evidence
- human_review_requirement

Recommended action must be one of: approve, hold, escalate, reject.
