#!/usr/bin/env bash
set -euo pipefail

# Preview the dev infrastructure changes without deploying resources.
az deployment sub what-if \
  --name fraud-ai-dev-what-if \
  --location eastus \
  --template-file infra/bicep/main.bicep \
  --parameters @infra/bicep/parameters/dev.parameters.json
