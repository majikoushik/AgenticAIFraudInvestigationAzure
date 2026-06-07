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

// Search indexes are intentionally managed by rag/indexes/*.py scripts.
// This keeps index schema evolution independent from base infrastructure deployment.

output searchServiceName string = search.name
output searchEndpoint string = 'https://${search.name}.search.windows.net'
output policyIndexName string = 'fraud-policies'
output historicalCaseIndexName string = 'historical-fraud-cases'
output caseEvidenceIndexName string = 'case-evidence'
