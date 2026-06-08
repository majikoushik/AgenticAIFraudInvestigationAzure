# Infrastructure

The Bicep scaffold deploys Azure resources for the fraud investigation MVP. Production hardening uses user-assigned managed identity, Key Vault-backed secret names, public network access toggles, and private endpoint/RBAC scaffolding.

Do not place secret values in parameter files. Use Key Vault and secure pipeline variable groups.

## Retention and Compliance Storage

The storage module includes placeholder private containers for `compliance-exports`, `archives`, and `retention-reports`. `storage-lifecycle-management.bicep` documents lifecycle, cool/archive tier, immutable storage, and legal hold controls that must be approved by compliance before production enablement. Cosmos DB TTL should be configured per container only after legal review.
