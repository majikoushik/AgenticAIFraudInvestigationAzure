# Infrastructure

The Bicep scaffold deploys Azure resources for the fraud investigation MVP. Production hardening uses user-assigned managed identity, Key Vault-backed secret names, public network access toggles, and private endpoint/RBAC scaffolding.

Do not place secret values in parameter files. Use Key Vault and secure pipeline variable groups.
