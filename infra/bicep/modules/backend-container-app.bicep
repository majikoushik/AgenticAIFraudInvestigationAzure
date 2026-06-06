param namePrefix string
param location string
param containerAppEnvironmentId string
param managedIdentityId string
param managedIdentityClientId string
param acrLoginServer string
param imageName string
param environmentName string
param cosmosDbDatabaseName string
param cosmosDbContainerName string
param aiSearchServiceName string
param serviceBusQueueName string
@secure()
param applicationInsightsConnectionString string
param tags object

resource app 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${namePrefix}-backend-ca'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: managedIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: imageName
          env: [
            {
              name: 'ENVIRONMENT'
              value: environmentName
            }
            {
              name: 'COSMOS_DB_DATABASE_NAME'
              value: cosmosDbDatabaseName
            }
            {
              name: 'COSMOS_DB_CONTAINER_NAME'
              value: cosmosDbContainerName
            }
            {
              name: 'AZURE_SEARCH_SERVICE_NAME'
              value: aiSearchServiceName
            }
            {
              name: 'SERVICE_BUS_QUEUE_NAME'
              value: serviceBusQueueName
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: applicationInsightsConnectionString
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: managedIdentityClientId
            }
          ]
          resources: {
            cpu: 0.5
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

output containerAppName string = app.name
output fqdn string = app.properties.configuration.ingress.fqdn
