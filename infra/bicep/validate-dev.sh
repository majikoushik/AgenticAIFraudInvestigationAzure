#!/usr/bin/env bash
set -euo pipefail

# Validate the dev subscription-scoped Bicep deployment.
# Replace the location and subscription context as needed before running.
az deployment sub validate \
  --name fraud-ai-dev-validate \
  --location eastus \
  --template-file infra/bicep/main.bicep \
  --parameters @infra/bicep/parameters/dev.parameters.json
