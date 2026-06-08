#!/usr/bin/env bash
set -euo pipefail
grep -R "publicNetworkAccess" infra/bicep/modules
echo "Public network access settings found for review."
