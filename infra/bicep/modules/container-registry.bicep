param namePrefix string
param location string
param skuName string
param acrPullPrincipalId string
param tags object

var registryName = replace('${namePrefix}acr', '-', '')

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: registryName
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource acrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(acrPullPrincipalId)) {
  name: guid(registry.id, acrPullPrincipalId, 'acrpull')
  scope: registry
  properties: {
    principalId: acrPullPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalType: 'ServicePrincipal'
  }
}

output registryResourceId string = registry.id
output registryName string = registry.name
output loginServer string = registry.properties.loginServer
