#!/usr/bin/env bash
set -euo pipefail
grep -q "Key Vault Secrets User" docs/deployment-hardening-key-vault-private-endpoints-managed-identity.md
test -f infra/bicep/modules/role-assignments.bicep
echo "RBAC assignment module and documentation are present."
