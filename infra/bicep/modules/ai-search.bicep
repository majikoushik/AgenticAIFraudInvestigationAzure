param namePrefix string
param location string
param skuName string
param tags object

resource search 'Microsoft.Search/searchServices@2023-11-01' = {
  name: '${namePrefix}-search'
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
  }
}

// Search indexes are intentionally not created in Bicep.
// They should be created by deployment scripts after the app policy schema is finalized.

output searchServiceName string = search.name
output searchEndpoint string = 'https://${search.name}.search.windows.net'
