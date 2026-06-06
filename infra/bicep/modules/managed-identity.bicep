param namePrefix string
param location string
param tags object

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${namePrefix}-mi'
  location: location
  tags: tags
}

// Role assignment placeholders to evaluate later:
// - Key Vault Secrets User
// - Storage Blob Data Contributor
// - Azure AI Search data-plane access
// - Cosmos DB SQL data access
// - AcrPull is assigned in main.bicep for Container Apps image pulls.

output identityResourceId string = identity.id
output principalId string = identity.properties.principalId
output clientId string = identity.properties.clientId
