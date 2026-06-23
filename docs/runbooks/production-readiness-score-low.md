# Runbook: Production Readiness Score Low

## Alert Summary
A production readiness assessment has an overall score below the configured threshold (default: 80/100). Deployment to production should not proceed without investigation.

## Severity
**SEV2 — Medium**

## Trigger Condition
`overall_score < 80` in a readiness assessment event.

## Immediate Actions

1. **View the assessment**
   - Log in to the fraud investigation platform as ADMIN or COMPLIANCE_OFFICER.
   - Navigate to **Production Readiness → Assessments**.
   - Open the latest assessment.

2. **Identify problem areas**
   - Review the **Category Score Grid** for categories below 60%.
   - Review **Warning** items across all categories.
   - Review **Manual Review Required** items.

3. **Prioritize HIGH-severity items**
   - Address HIGH-severity WARNINGs and FAILs before reviewing MEDIUM/LOW items.

## Resolution Steps

1. For each category with score < 60:
   - Review the failing and warning checks in that category.
   - Assign owners and remediation plans.
   - Add evidence for manual checks where verification is complete.

2. For manual review items:
   - Collect evidence from the appropriate team (security scan output, legal review, etc.).
   - Add evidence via: `POST /api/v1/readiness/assessments/{id}/evidence`.

3. Re-run the assessment after fixes: `POST /api/v1/readiness/assessments/run`.

4. Target score: ≥ 90 for READY decision; ≥ 70 for READY_WITH_RISKS.

## Score Interpretation

| Score | Status |
| --- | --- |
| ≥ 90 | READY |
| 70–89 | READY_WITH_RISKS (requires risk register review) |
| 50–69 | MANUAL_REVIEW_REQUIRED |
| < 50 | NOT_READY |

## Related Documents
- [End-to-End Production Readiness Checklist](../end-to-end-production-readiness-checklist.md)
- [Readiness Blocker Runbook](./production-readiness-blocker-found.md)
