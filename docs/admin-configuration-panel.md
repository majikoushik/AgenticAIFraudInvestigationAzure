# Admin Configuration Panel

The Admin Configuration Panel provides a safe interface for authorized administrators to inspect and update non-secret runtime settings in local MVP mode.

## What Admins Can Manage

- AI provider mode and safety toggles
- Azure OpenAI and Azure AI Foundry non-secret settings
- RAG retrieval settings
- Human review workflow settings
- Alert thresholds
- Cost monitoring thresholds
- Observability settings
- Feature flags
- Local/demo mode behavior

## What Admins Cannot Manage

The panel never displays or edits API keys, Azure Search keys, Azure OpenAI keys, connection strings, webhook URLs, SMTP credentials, JWTs, or tokens. Secrets must be managed through Key Vault, secure deployment variables, or a future enterprise secrets workflow.

## Safe Registry

The backend uses an explicit allow-list registry in `backend/app/admin/admin_config_schema.py`. It does not scan arbitrary environment variables. Unknown keys are rejected.

Each registry item defines category, data type, default value, editability, allowed values, min/max values, restart requirement, and description.

## Local Store

Local overrides are stored in:

```text
data/synthetic/admin_config.json
```

History records are stored in:

```text
data/synthetic/admin_config_history.json
```

Only non-secret overrides are stored.

## Validation

Updates are validated by `AdminConfigValidator`:

- key must exist in the safe registry
- item must be editable
- item must not be secret
- value type must match the declared type
- enum values must match allowed values
- numeric values must satisfy min/max
- suspicious secret-like values are rejected

## Audit And Telemetry

Configuration views, updates, resets, feature flag updates, and validation failures emit audit events and local telemetry where available. Secret values are masked before audit or history writes.

## APIs

Admin endpoints require `ADMIN_CONFIG` permission:

- `GET /api/v1/admin/config`
- `GET /api/v1/admin/config/{category}`
- `PATCH /api/v1/admin/config`
- `POST /api/v1/admin/config/reset`
- `GET /api/v1/admin/config/history`
- `GET /api/v1/admin/config/health`
- `GET /api/v1/admin/feature-flags`
- `PATCH /api/v1/admin/feature-flags/{flag_key}`

Example update:

```json
{
  "updates": [
    {
      "key": "RAG_TOP_K",
      "value": 8
    }
  ],
  "comment": "Tune retrieval top-k."
}
```

## Frontend

The panel is available at:

```text
http://localhost:3000/admin/config
```

It shows health, category tabs, item editors, feature flags, validation errors, reset controls, secret redaction notice, and history.

## Azure App Configuration And Key Vault

The MVP includes disabled placeholders for Azure App Configuration and Key Vault. Production integration should use managed identity, keep non-secret settings in Azure App Configuration, and keep all secrets in Key Vault.

## Local Verification

1. Start backend and frontend.
2. Log in as `ADMIN`.
3. Open `/admin/config`.
4. Change `RAG_TOP_K`.
5. Confirm the history table records the change.
6. Toggle a feature flag.
7. Reset local overrides.

## Production Recommendations

- Keep backend ADMIN enforcement as the source of truth.
- Do not rely on frontend role checks for security.
- Use Key Vault for all secrets.
- Use Azure App Configuration for production non-secret settings.
- Require change comments and review for production changes.
- Monitor audit events for configuration drift.
