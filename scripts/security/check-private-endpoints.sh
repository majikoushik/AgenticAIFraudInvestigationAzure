#!/usr/bin/env bash
set -euo pipefail
test -f infra/bicep/modules/private-endpoints.bicep
test -f infra/bicep/modules/private-dns-zones.bicep
echo "Private endpoint and DNS modules are present."
