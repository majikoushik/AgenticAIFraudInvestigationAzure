# Reviewer Prompt

Validate whether the investigation summary is supported by retrieved evidence and policy citations.

Return JSON with:

```json
{
  "is_evidence_supported": true,
  "unsupported_claims": [],
  "citation_issues": [],
  "policy_alignment": "ALIGNED | PARTIALLY_ALIGNED | NOT_ALIGNED | UNKNOWN",
  "human_review_required": true,
  "safety_flags": [],
  "reviewer_notes": ""
}
```
