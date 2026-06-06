param namePrefix string
param location string
param tags object

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${namePrefix}-law'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

output workspaceResourceId string = workspace.id
output customerId string = workspace.properties.customerId
output sharedKey string = listKeys(workspace.id, workspace.apiVersion).primarySharedKey
