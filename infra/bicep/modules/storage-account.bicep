param namePrefix string
param location string
param publicNetworkAccess string = 'Enabled'
param tags object

var storageAccountName = replace('${namePrefix}st', '-', '')

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    publicNetworkAccess: publicNetworkAccess
  }
}

resource evidenceContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/evidence'
  properties: {
    publicAccess: 'None'
  }
}

resource complianceExportsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/compliance-exports'
  properties: {
    publicAccess: 'None'
  }
}

resource archivesContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/archives'
  properties: {
    publicAccess: 'None'
  }
}

resource retentionReportsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/retention-reports'
  properties: {
    publicAccess: 'None'
  }
}

// Production note: configure immutable storage/legal holds and lifecycle rules
// only after compliance approval. See storage-lifecycle-management.bicep.

output storageAccountName string = storage.name
output storageAccountResourceId string = storage.id
