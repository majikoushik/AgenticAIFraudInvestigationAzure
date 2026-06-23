# Pipelines

The provided Azure DevOps YAML (`azure-pipelines.yml`) acts as a **validation pipeline and deployment template**.

## Validation (Implemented)
- Builds and lints the Next.js frontend.
- Builds the FastAPI backend and runs Python tests (`pytest`).
- Validates Bicep infrastructure templates using offline structural validation (`az bicep build`).
- Scans for hardcoded secrets.

## Deployment (Templates / Placeholders)
The deployment stages (pushing images to ACR, updating Container Apps, and executing `az deployment sub create`) are **templates/placeholders**. They use `echo` commands and placeholder service connections.

To use this pipeline for real deployment, you must:
1. Configure an Azure Service Connection.
2. Link a Key Vault-backed variable group.
3. Configure your ACR and Container Apps target details.
4. Replace the `echo` commands in the deployment stages with real Docker and Azure CLI commands.
