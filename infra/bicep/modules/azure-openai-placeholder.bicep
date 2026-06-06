param namePrefix string
param location string
param deployAzureOpenAIPlaceholder bool
param tags object

resource account 'Microsoft.CognitiveServices/accounts@2023-05-01' = if (deployAzureOpenAIPlaceholder) {
  name: '${namePrefix}-aoai'
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

// MVP placeholder:
// Azure OpenAI / Azure AI Foundry deployments are disabled by default because service
// availability, quota, and model deployment names are environment-specific.
// Add model deployments later through secure scripts or AI Foundry workflows.

output accountName string = account.?name ?? '${namePrefix}-aoai-placeholder'
output accountEndpoint string = account.?properties.endpoint ?? 'not-deployed'
