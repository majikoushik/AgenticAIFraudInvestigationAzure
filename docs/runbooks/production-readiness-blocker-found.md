# Runbook: Production Readiness Blocker Found

## Alert Summary
A production readiness assessment has detected one or more **BLOCKER**-severity check failures. The system cannot be deployed to production until all blockers are resolved.

## Severity
**SEV1 — High**

## Trigger Condition
`blocking_issue_count > 0` in a readiness assessment event.

## Immediate Actions

1. **Identify the blockers**
   - Log in to the fraud investigation platform as ADMIN.
   - Navigate to **Production Readiness → Assessments**.
   - Open the latest assessment.
   - Review the **Blocking Issues** panel.

2. **Review the risk register**
   - Navigate to **Production Readiness → Risk Register**.
   - Verify that risks have been created for each blocker.
   - Assign an owner and mitigation plan to each risk.

3. **Escalate to the appropriate team**
   - `SECURITY` blockers → Security Team
   - `IDENTITY_AND_ACCESS` blockers → Identity Team
   - `AI_SAFETY_AND_GUARDRAILS` blockers → AI Governance Team
   - `DEVOPS_AND_RELEASE_MANAGEMENT` blockers → DevOps Team
   - `SECRETS_AND_KEY_MANAGEMENT` blockers → Platform Team

4. **Do not proceed with production deployment** until all blockers are resolved and the risk register is updated.

## Resolution Steps

1. Fix the root cause of each BLOCKER check failure.
2. Re-run the readiness assessment: `POST /api/v1/readiness/assessments/run`.
3. Confirm `blocking_issue_count == 0` and `go_live_decision != NOT_READY`.
4. Update risk statuses to MITIGATED or CLOSED.
5. Export the readiness report and share with the platform team sign-off chain.

## Contacts

| Role | Action |
| --- | --- |
| Solution Architect | Overall go-live decision |
| Security Owner | SEC/KEY/IAM blocker resolution |
| AI Governance Team | AI/GUARDRAIL blocker resolution |
| Platform Owner | Infrastructure blockers |
| Fraud Ops Lead | HITL/business blockers |

## Related Documents
- [End-to-End Production Readiness Checklist](../end-to-end-production-readiness-checklist.md)
- [Production Security Checklist](../production-security-checklist.md)
- [Deployment Hardening Guide](../deployment-hardening-key-vault-private-endpoints-managed-identity.md)
