# Azure Bicep Infrastructure

Modular Azure infrastructure for the `agentic-ai-fraud-investigation-azure` MVP.

The deployment is subscription-scoped because `main.bicep` creates the resource group and then deploys all resource modules into that group.

## Resources

- Resource group
- Azure Container Registry
- Azure Container Apps environment
- Backend Container App
- Frontend Container App
- User-assigned managed identity
- Key Vault
- Storage account
- Cosmos DB account, SQL database, and `fraudCases` container
- Azure AI Search service
- Azure OpenAI / AI Foundry placeholder
- Log Analytics Workspace
- Application Insights
- Service Bus namespace and fraud alert queue
- Basic VNet placeholder

## Prerequisites

- Azure CLI
- Bicep CLI, or Azure CLI with built-in Bicep support
- Azure subscription selected with `az account set`
- Permissions to create resource groups and the listed resources
- Permissions to create role assignments for managed identity access

## Login

```bash
az login
az account set --subscription "<subscription-id-or-name>"
```

## Validate Dev

```bash
./infra/bicep/validate-dev.sh
```

PowerShell equivalent:

```powershell
az deployment sub validate `
  --name fraud-ai-dev-validate `
  --location eastus `
  --template-file infra/bicep/main.bicep `
  --parameters "@infra/bicep/parameters/dev.parameters.json"
```

## What-If Dev

```bash
./infra/bicep/what-if-dev.sh
```

## Deploy Dev

```bash
./infra/bicep/deploy-dev.sh
```

PowerShell:

```powershell
./infra/bicep/deploy-dev.ps1
```

## Deploy Test Or Prod

Use the matching parameter file:

```bash
az deployment sub create \
  --name fraud-ai-test-deploy \
  --location eastus \
  --template-file infra/bicep/main.bicep \
  --parameters @infra/bicep/parameters/test.parameters.json
```

```bash
az deployment sub create \
  --name fraud-ai-prod-deploy \
  --location eastus \
  --template-file infra/bicep/main.bicep \
  --parameters @infra/bicep/parameters/prod.parameters.json
```

## Secrets

No real secrets are deployed by Bicep.

Add secrets manually through Key Vault, or from secure pipeline variables, after deployment:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_SEARCH_ENDPOINT`
- `COSMOS_CONNECTION_STRING`
- `AUTH_MODE`
- `ENTRA_TENANT_ID`
- `ENTRA_CLIENT_ID`
- `ENTRA_API_AUDIENCE`
- `ENTRA_AUTHORITY`
- `NEXT_PUBLIC_AUTH_MODE`
- `NEXT_PUBLIC_ENTRA_CLIENT_ID`
- `NEXT_PUBLIC_ENTRA_TENANT_ID`
- `NEXT_PUBLIC_ENTRA_AUTHORITY`
- `NEXT_PUBLIC_API_SCOPE`

Prefer managed identity over connection strings wherever supported.

## Azure OpenAI Placeholder

`deployAzureOpenAIPlaceholder` is disabled by default. Enable it only in regions and subscriptions where Azure OpenAI is available and approved. Model deployments are intentionally not created in Bicep for this MVP.

## Microsoft Entra ID Placeholders

This MVP does not create Entra app registrations in Bicep. Create them manually or through a governed identity pipeline, then pass the resulting values to Container Apps as environment variables:

- Frontend app registration client ID for `NEXT_PUBLIC_ENTRA_CLIENT_ID`
- Backend API app registration application ID URI for `ENTRA_API_AUDIENCE` and `NEXT_PUBLIC_API_SCOPE`
- Tenant ID for backend and frontend auth settings
- App roles such as `Fraud.Analyst`, `Fraud.Manager`, `Compliance.Officer`, `Auditor`, and `Admin`

Assign users or groups to Entra app roles before enabling `AUTH_MODE=entra`.

## Required Permissions

The deploying principal should have:

- Contributor at subscription or target deployment scope
- User Access Administrator or Owner when creating role assignments
- Permission to register resource providers if not already registered

Recommended providers:

- `Microsoft.App`
- `Microsoft.ContainerRegistry`
- `Microsoft.KeyVault`
- `Microsoft.Storage`
- `Microsoft.DocumentDB`
- `Microsoft.Search`
- `Microsoft.CognitiveServices`
- `Microsoft.Insights`
- `Microsoft.OperationalInsights`
- `Microsoft.ManagedIdentity`
- `Microsoft.ServiceBus`
- `Microsoft.Network`

## Notes

- Container images are placeholders until the CI/CD pipeline builds and pushes real images to ACR.
- Search indexes are not created in Bicep. Add them later with scripts once the schema is stable.
- Networking is represented as a placeholder VNet. Wire Container Apps into the VNet when private networking is required.
