# Microsoft Entra ID Authentication

This MVP supports enterprise-ready authentication with two modes:

- `local`: development-only demo auth using headers.
- `entra`: Microsoft Entra ID-ready JWT validation and frontend MSAL structure.

## Local Auth Mode

Set:

```env
AUTH_MODE=local
NEXT_PUBLIC_AUTH_MODE=local
```

The frontend `/login` page lets you select a demo role. The API client sends:

```text
X-Demo-User
X-Demo-Role
X-Demo-Email
```

If headers are missing, the backend defaults to `local_demo_user` with `FRAUD_ANALYST`. Local auth is for development only and must not be used in production.

## Entra Auth Mode

Set:

```env
AUTH_MODE=entra
ENTRA_TENANT_ID=
ENTRA_CLIENT_ID=
ENTRA_API_AUDIENCE=
ENTRA_AUTHORITY=https://login.microsoftonline.com/{tenant_id}
NEXT_PUBLIC_AUTH_MODE=entra
NEXT_PUBLIC_ENTRA_CLIENT_ID=
NEXT_PUBLIC_ENTRA_TENANT_ID=
NEXT_PUBLIC_ENTRA_AUTHORITY=
NEXT_PUBLIC_ENTRA_REDIRECT_URI=http://localhost:3000
NEXT_PUBLIC_API_SCOPE=api://<backend-api-client-id>/access_as_user
```

The frontend auth structure is MSAL-ready. The backend validates Bearer JWT access tokens against Entra OpenID metadata and JWKS signing keys.

## Role Mapping

Entra app roles map to internal roles:

- `Fraud.Analyst` -> `FRAUD_ANALYST`
- `Fraud.Manager` -> `FRAUD_MANAGER`
- `Compliance.Officer` -> `COMPLIANCE_OFFICER`
- `Auditor` -> `AUDITOR`
- `Admin` -> `ADMIN`

## Permission Matrix

- `FRAUD_ANALYST`: view cases, run AI investigation, submit hold/escalate/reject, view audit, view metrics.
- `FRAUD_MANAGER`: analyst permissions plus approve and close cases.
- `COMPLIANCE_OFFICER`: view cases, run investigation, submit hold/escalate, close cases, view audit and metrics.
- `AUDITOR`: read-only access to cases, audit, and metrics.
- `ADMIN`: full access and admin config.

## Protected Endpoints

Public:

- `GET /health`
- `GET /api/v1/auth/mode`

Protected:

- `/api/v1/cases`
- `/api/v1/cases/{case_id}`
- `/api/v1/cases/{case_id}/investigate`
- `/api/v1/cases/{case_id}/review`
- `/api/v1/cases/{case_id}/close`
- `/api/v1/cases/{case_id}/audit`
- `/api/v1/audit/*`
- `/api/v1/metrics/*`
- `/api/v1/agents/config` requires `ADMIN`

## Local Role Testing

1. Start the app with `AUTH_MODE=local`.
2. Open `http://localhost:3000/login`.
3. Select `AUDITOR` and confirm decision submission is unavailable.
4. Select `FRAUD_ANALYST` and confirm `APPROVE` is unavailable.
5. Select `FRAUD_MANAGER` and confirm `APPROVE` is available.
6. Select `ADMIN` and confirm admin config APIs are allowed.

## Manual Entra Setup

1. Create a frontend SPA app registration.
2. Create a backend API app registration.
3. Expose an API scope such as `access_as_user`.
4. Add app roles listed above.
5. Assign users or groups to app roles.
6. Configure frontend and backend environment variables.
7. Set `AUTH_MODE=entra` and `NEXT_PUBLIC_AUTH_MODE=entra`.

## Future Production Improvements

- Enforce app roles and group-to-role mapping through governance.
- Add Conditional Access policies.
- Use managed identities for Azure service access.
- Validate JWTs at Azure API Management before backend ingress.
- Stream auth and audit logs to Log Analytics and Microsoft Sentinel.
