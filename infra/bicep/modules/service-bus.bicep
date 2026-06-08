param namePrefix string
param location string
param queueName string
param publicNetworkAccess string = 'Enabled'
param tags object

resource namespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: '${namePrefix}-sb'
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    publicNetworkAccess: publicNetworkAccess
    disableLocalAuth: false // TODO: switch to true when every client uses managed identity.
  }
}

resource queue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: namespace
  name: queueName
  properties: {
    lockDuration: 'PT1M'
    maxDeliveryCount: 10
    requiresDuplicateDetection: false
    requiresSession: false
  }
}

output namespaceName string = namespace.name
output namespaceResourceId string = namespace.id
output queueName string = queue.name
