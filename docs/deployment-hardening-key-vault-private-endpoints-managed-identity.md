# Deployment Hardening: Key Vault, Private Endpoints, Managed Identity

This guide describes the Azure-ready hardening approach for the fraud investigation MVP. Local mode remains JSON and environment based; production mode should use managed identity, Azure Key Vault, RBAC, private endpoints, and no secret values in source control or pipeline YAML.

## Local vs Production

Local mode uses `DEPLOYMENT_MODE=local`, `SECRET_PROVIDER=environment`, and placeholder values only. Production should set `DEPLOYMENT_MODE=prod`, `USE_MANAGED_IDENTITY=true`, `KEY_VAULT_ENABLED=true`, and `SECRET_PROVIDER=key_vault`.

## Secret Handling

Secret values must be stored in Azure Key Vault, not `.env.example`, Bicep parameter files, or Azure DevOps YAML. Secret name variables are allowed, for example `AZURE_OPENAI_API_KEY_SECRET_NAME=fraud-ai-azure-openai-api-key`.

Store these values in Key Vault when needed:

- Azure OpenAI endpoint and API key when managed identity is unavailable
- Azure AI Search query/admin keys when RBAC is unavailable
- Cosmos, Storage, and Service Bus connection strings during transition to RBAC clients
- Application Insights connection string
- Teams webhook URL
- SMTP password

## Managed Identity

The backend Container App uses a user-assigned managed identity. Runtime access should receive least-privilege roles such as Key Vault Secrets User, Search Index Data Reader, Storage Blob Data Reader/Contributor, Service Bus Data Sender/Receiver, and Cognitive Services OpenAI User.

Use a separate ingestion/admin identity for index creation and elevated operations when moving beyond the MVP.

## Private Endpoints and DNS

Private endpoint scaffolding exists for Key Vault, Storage Blob, Cosmos DB SQL, Azure AI Search, Azure OpenAI/Cognitive Services, Service Bus, and ACR. Private DNS zones are scaffolded for the matching `privatelink` domains.

Set `privateEndpointsEnabled=true` and `disablePublicNetworkAccess=true` for production after VNet/subnet and DNS zone group wiring are validated.

## RBAC Matrix

| Resource | Runtime role |
| --- | --- |
| Key Vault | Key Vault Secrets User |
| ACR | AcrPull |
| Storage | Storage Blob Data Reader or Contributor |
| Service Bus | Data Sender and Data Receiver |
| Azure AI Search | Search Index Data Reader |
| Azure OpenAI | Cognitive Services OpenAI User |
| Cosmos DB | Cosmos DB data contributor equivalent, configured with data-plane RBAC |

## Deployment

1. Create Key Vault secret values manually or through an approved secure process.
2. Deploy Bicep with environment parameters.
3. Confirm Container Apps receive only secret names, Key Vault URI, and managed identity config.
4. Validate `/api/v1/security/health`.
5. Run `scripts/security/check-no-secrets.ps1` or `.sh`.

## Known MVP Limitations

- Private endpoint module is scaffolded and needs endpoint resource creation/zone groups wired per landing zone.
- Some runtime clients still use local JSON or environment settings until Azure SDK clients are introduced.
- Cosmos DB data-plane RBAC requires additional role definition work.
- Fully private backend ingress should be paired with API Management or equivalent.

## Future Improvements

Azure App Configuration, Key Vault references in Container Apps, private ingress with API Management, Azure Firewall/NAT, Defender for Cloud, Sentinel, Azure Policy, separate runtime/ingestion identities, and secret rotation automation.
