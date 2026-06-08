param namePrefix string
param location string
param purgeProtectionEnabled bool
param publicNetworkAccess string = 'Enabled'
param tags object

var keyVaultName = '${namePrefix}-kv'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    tenantId: tenant().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableSoftDelete: true
    enablePurgeProtection: purgeProtectionEnabled
    enableRbacAuthorization: true
    publicNetworkAccess: publicNetworkAccess
  }
}

// Placeholder secret names only. Do not deploy real secret values in Bicep:
// - AZURE_OPENAI_ENDPOINT
// - AZURE_OPENAI_API_KEY
// - AZURE_SEARCH_ENDPOINT
// - COSMOS_CONNECTION_STRING

output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output keyVaultResourceId string = keyVault.id
