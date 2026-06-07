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
param observabilityEnabled string = 'true'
param logLevel string = 'INFO'
param telemetryEnvironment string = environmentName
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
              name: 'OBSERVABILITY_ENABLED'
              value: observabilityEnabled
            }
            {
              name: 'OBSERVABILITY_MODE'
              value: 'azure_monitor'
            }
            {
              name: 'TELEMETRY_ENVIRONMENT'
              value: telemetryEnvironment
            }
            {
              name: 'LOG_LEVEL'
              value: logLevel
            }
            {
              name: 'LOG_FORMAT'
              value: 'json'
            }
            {
              name: 'TELEMETRY_SERVICE_NAME'
              value: 'fraud-investigation-platform'
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: managedIdentityClientId
            }
            {
              name: 'AI_PROVIDER'
              value: 'local'
            }
            {
              name: 'AI_PROVIDER_ALLOW_FALLBACK'
              value: 'true'
            }
            {
              name: 'AZURE_OPENAI_CHAT_DEPLOYMENT'
              value: 'gpt-4o-mini'
            }
            {
              name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT'
              value: 'text-embedding-3-small'
            }
            {
              name: 'LLM_ENABLE_JSON_MODE'
              value: 'true'
            }
            {
              name: 'LLM_LOG_PROMPTS'
              value: 'false'
            }
            {
              name: 'LLM_LOG_RESPONSES'
              value: 'false'
            }
            {
              name: 'AI_SAFETY_REQUIRE_HUMAN_REVIEW'
              value: 'true'
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
