# Infrastructure

Azure Bicep placeholders define the production-oriented Azure shape for the MVP.

Admin configuration support is intentionally non-secret:

- `ADMIN_CONFIG_ENABLED`
- `ADMIN_CONFIG_MODE`
- safe feature flag defaults
- Azure App Configuration placeholder toggle
- Key Vault placeholder toggle

Secrets must be stored in Key Vault or supplied through secure pipeline variables. The Admin Configuration Panel manages only safe non-secret runtime overrides. Production deployments should use Azure App Configuration for non-secret settings and Key Vault for secret references.
