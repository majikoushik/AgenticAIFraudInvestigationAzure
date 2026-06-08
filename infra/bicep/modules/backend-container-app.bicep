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
param alertingEnabled string = 'true'
param costMonitoringEnabled string = 'true'
param adminConfigEnabled string = 'true'
param caseAssignmentEnabled string = 'true'
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
            {
              name: 'ALERTING_ENABLED'
              value: alertingEnabled
            }
            {
              name: 'ALERTING_MODE'
              value: 'local'
            }
            {
              name: 'NOTIFICATIONS_ENABLED'
              value: 'false'
            }
            {
              name: 'INCIDENT_AUTO_CREATE_ENABLED'
              value: 'true'
            }
            {
              name: 'COST_MONITORING_ENABLED'
              value: costMonitoringEnabled
            }
            {
              name: 'COST_MONITORING_MODE'
              value: 'local'
            }
            {
              name: 'CURRENCY'
              value: 'USD'
            }
            {
              name: 'DEFAULT_INPUT_TOKEN_COST_PER_1K'
              value: '0.0000'
            }
            {
              name: 'DEFAULT_OUTPUT_TOKEN_COST_PER_1K'
              value: '0.0000'
            }
            {
              name: 'TOKEN_DAILY_LIMIT'
              value: '1000000'
            }
            {
              name: 'COST_DAILY_BUDGET_LIMIT'
              value: '50'
            }
            {
              name: 'COST_MONTHLY_BUDGET_LIMIT'
              value: '1000'
            }
            {
              name: 'AZURE_COST_MANAGEMENT_ENABLED'
              value: 'false'
            }
            {
              name: 'ADMIN_CONFIG_ENABLED'
              value: adminConfigEnabled
            }
            {
              name: 'ADMIN_CONFIG_MODE'
              value: 'local'
            }
            {
              name: 'CASE_ASSIGNMENT_ENABLED'
              value: caseAssignmentEnabled
            }
            {
              name: 'CASE_ASSIGNMENT_MODE'
              value: 'local'
            }
            {
              name: 'DEFAULT_ASSIGNMENT_TEAM'
              value: 'Fraud Operations'
            }
            {
              name: 'DEFAULT_ASSIGNMENT_PRIORITY'
              value: 'MEDIUM'
            }
            {
              name: 'SLA_LOW_PRIORITY_HOURS'
              value: '72'
            }
            {
              name: 'SLA_MEDIUM_PRIORITY_HOURS'
              value: '48'
            }
            {
              name: 'SLA_HIGH_PRIORITY_HOURS'
              value: '24'
            }
            {
              name: 'SLA_CRITICAL_PRIORITY_HOURS'
              value: '4'
            }
            {
              name: 'AUTO_SET_SLA_ON_ASSIGNMENT'
              value: 'true'
            }
            {
              name: 'ALLOW_SELF_ASSIGNMENT'
              value: 'true'
            }
            {
              name: 'ALLOW_ANALYST_RELEASE_OWN_CASE'
              value: 'true'
            }
            {
              name: 'WORKLOAD_HIGH_THRESHOLD'
              value: '15'
            }
            {
              name: 'WORKLOAD_CRITICAL_THRESHOLD'
              value: '20'
            }
            {
              name: 'FEATURE_ENABLE_AGENTIC_INVESTIGATION'
              value: 'true'
            }
            {
              name: 'FEATURE_ENABLE_HUMAN_REVIEW'
              value: 'true'
            }
            {
              name: 'FEATURE_ENABLE_COST_DASHBOARD'
              value: 'true'
            }
            {
              name: 'FEATURE_ENABLE_OBSERVABILITY_PAGE'
              value: 'true'
            }
            {
              name: 'FEATURE_ENABLE_CASE_ASSIGNMENT'
              value: caseAssignmentEnabled
            }
            {
              name: 'FEATURE_ENABLE_AZURE_SEARCH_RAG'
              value: 'false'
            }
            {
              name: 'FEATURE_ENABLE_AZURE_OPENAI'
              value: 'false'
            }
            {
              name: 'AZURE_APP_CONFIGURATION_ENABLED'
              value: 'false'
            }
            {
              name: 'AZURE_KEY_VAULT_ENABLED'
              value: 'false'
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
