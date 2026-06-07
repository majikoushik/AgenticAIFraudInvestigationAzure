# Auth Failure Spike

## Alert meaning
Authentication failures increased above the expected baseline.

## Severity
SEV1_HIGH.

## Possible causes
Entra ID configuration drift, expired tokens, invalid issuer/audience settings, suspicious login attempts, or frontend auth mismatch.

## Immediate triage steps
Check recent identity changes, failed principals, source IPs, and whether admins are locked out.

## KQL queries to run
Run `monitoring/kql/auth-failure-spike.kql`.

## Application logs to check
Inspect `AUTHENTICATION_FAILED`, request headers metadata, and correlation IDs.

## Azure resources to inspect
Microsoft Entra ID app registration, Container Apps configuration, Key Vault references, and Application Insights.

## Safe mitigation steps
Revert identity config changes, validate token settings, and temporarily restrict suspicious sources if needed.

## Escalation path
Security operations and identity platform owner.

## When to resolve
Resolve after failed authentication volume returns to baseline and valid users can authenticate.

## Post-incident review notes
Document impacted roles, identity changes, and any suspicious access pattern.
