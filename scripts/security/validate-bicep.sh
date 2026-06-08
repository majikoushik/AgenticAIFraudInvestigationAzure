#!/usr/bin/env bash
set -euo pipefail
az bicep build --file infra/bicep/main.bicep
