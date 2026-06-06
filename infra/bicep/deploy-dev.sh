#!/usr/bin/env bash
set -euo pipefail

# Deploy the dev MVP infrastructure.
# Assumes `az login` and the correct subscription are already selected.
az deployment sub create \
  --name fraud-ai-dev-deploy \
  --location eastus \
  --template-file infra/bicep/main.bicep \
  --parameters @infra/bicep/parameters/dev.parameters.json
