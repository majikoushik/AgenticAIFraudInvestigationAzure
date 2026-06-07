# Authorization Failure Spike

## Alert meaning
Authenticated users are being denied access more often than expected.

## Severity
SEV2_MEDIUM.

## Possible causes
Role mapping changes, admin policy drift, missing claims, incorrect route permissions, or frontend role assumptions.

## Immediate triage steps
Identify denied routes, affected roles, and recent authorization configuration changes.

## KQL queries to run
Run `monitoring/kql/authorization-failure-spike.kql`.

## Application logs to check
Inspect `AUTHORIZATION_FAILED`, user role claims, route names, and admin endpoint access.

## Azure resources to inspect
Entra app roles, API auth settings, Container Apps environment variables, and Application Insights.

## Safe mitigation steps
Restore expected role mappings, reissue tokens, and avoid bypassing admin controls.

## Escalation path
Identity owner and application security owner.

## When to resolve
Resolve after legitimate users regain expected access and unauthorized access remains blocked.

## Post-incident review notes
Record affected roles, changed permissions, and regression tests added.
