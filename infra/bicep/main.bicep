targetScope = 'subscription'

@description('Deployment environment name, such as dev, test, or prod.')
param environmentName string

@description('Azure region for the resource group and resources.')
param location string

@description('Short project name used for tagging and consistent resource naming.')
param projectName string

@description('Backend image name and tag, without registry login server.')
param backendImageName string

@description('Frontend image name and tag, without registry login server.')
param frontendImageName string

@description('Azure Container Registry SKU.')
param containerRegistrySku string

@description('Azure AI Search SKU.')
param aiSearchSku string

@description('Cosmos DB SQL database name.')
param cosmosDbDatabaseName string

@description('Cosmos DB SQL container name.')
param cosmosDbContainerName string

@description('Service Bus queue name for fraud alert intake.')
param serviceBusQueueName string

@description('Enable Key Vault purge protection. Use true for production.')
param keyVaultPurgeProtection bool = false

@description('Deploy Azure OpenAI account placeholder resource. Disabled by default for MVP portability.')
param deployAzureOpenAIPlaceholder bool = false

@description('Enable application observability middleware and telemetry.')
param observabilityEnabled string = 'true'

@description('Backend log level.')
param logLevel string = 'INFO'

@description('Telemetry environment label.')
param telemetryEnvironment string = environmentName

@description('Enable local or Azure-backed alerting configuration in the backend.')
param alertingEnabled string = 'true'

@description('Enable local estimated cost monitoring configuration in the backend. Pricing values should be supplied by environment or pipeline variables.')
param costMonitoringEnabled string = 'true'

@description('Enable safe non-secret admin configuration panel. Secrets must be stored in Key Vault or secure pipeline variables.')
param adminConfigEnabled string = 'true'

@description('Resource tags applied to all supported resources.')
param tags object

var namePrefix = 'fraud-ai-${environmentName}'
var resourceGroupName = '${namePrefix}-rg'
var backendContainerName = 'backend'
var frontendContainerName = 'frontend'

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: union(tags, {
    project: projectName
    environment: environmentName
  })
}

module logAnalytics 'modules/log-analytics.bicep' = {
  name: '${namePrefix}-log-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    tags: tags
  }
}

module appInsights 'modules/application-insights.bicep' = {
  name: '${namePrefix}-appi-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    workspaceResourceId: logAnalytics.outputs.workspaceResourceId
    tags: tags
  }
}

module identity 'modules/managed-identity.bicep' = {
  name: '${namePrefix}-id-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    tags: tags
  }
}

module registry 'modules/container-registry.bicep' = {
  name: '${namePrefix}-acr-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    skuName: containerRegistrySku
    acrPullPrincipalId: identity.outputs.principalId
    tags: tags
  }
}

module keyVault 'modules/key-vault.bicep' = {
  name: '${namePrefix}-kv-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    purgeProtectionEnabled: keyVaultPurgeProtection
    tags: tags
  }
}

module storage 'modules/storage-account.bicep' = {
  name: '${namePrefix}-st-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    tags: tags
  }
}

module cosmosDb 'modules/cosmos-db.bicep' = {
  name: '${namePrefix}-cosmos-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    databaseName: cosmosDbDatabaseName
    containerName: cosmosDbContainerName
    tags: tags
  }
}

module aiSearch 'modules/ai-search.bicep' = {
  name: '${namePrefix}-search-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    skuName: aiSearchSku
    tags: tags
  }
}

module serviceBus 'modules/service-bus.bicep' = {
  name: '${namePrefix}-sb-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    queueName: serviceBusQueueName
    tags: tags
  }
}

module networking 'modules/networking-placeholder.bicep' = {
  name: '${namePrefix}-net-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    tags: tags
  }
}

module openAiPlaceholder 'modules/azure-openai-placeholder.bicep' = {
  name: '${namePrefix}-aoai-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    deployAzureOpenAIPlaceholder: deployAzureOpenAIPlaceholder
    tags: tags
  }
}

module containerAppsEnvironment 'modules/container-apps-environment.bicep' = {
  name: '${namePrefix}-cae-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    logAnalyticsCustomerId: logAnalytics.outputs.customerId
    logAnalyticsSharedKey: logAnalytics.outputs.sharedKey
    tags: tags
  }
}

module backendApp 'modules/backend-container-app.bicep' = {
  name: '${namePrefix}-backend-ca-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    containerAppEnvironmentId: containerAppsEnvironment.outputs.environmentId
    managedIdentityId: identity.outputs.identityResourceId
    managedIdentityClientId: identity.outputs.clientId
    acrLoginServer: registry.outputs.loginServer
    imageName: '${registry.outputs.loginServer}/${backendImageName}'
    environmentName: environmentName
    cosmosDbDatabaseName: cosmosDbDatabaseName
    cosmosDbContainerName: cosmosDbContainerName
    aiSearchServiceName: aiSearch.outputs.searchServiceName
    serviceBusQueueName: serviceBusQueueName
    applicationInsightsConnectionString: appInsights.outputs.connectionString
    observabilityEnabled: observabilityEnabled
    logLevel: logLevel
    telemetryEnvironment: telemetryEnvironment
    alertingEnabled: alertingEnabled
    costMonitoringEnabled: costMonitoringEnabled
    adminConfigEnabled: adminConfigEnabled
    tags: tags
  }
}

module frontendApp 'modules/frontend-container-app.bicep' = {
  name: '${namePrefix}-frontend-ca-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    containerAppEnvironmentId: containerAppsEnvironment.outputs.environmentId
    managedIdentityId: identity.outputs.identityResourceId
    managedIdentityClientId: identity.outputs.clientId
    acrLoginServer: registry.outputs.loginServer
    imageName: '${registry.outputs.loginServer}/${frontendImageName}'
    backendApiBaseUrl: 'https://${backendApp.outputs.fqdn}'
    tags: tags
  }
}

module actionGroups 'modules/action-groups.bicep' = {
  name: '${namePrefix}-action-groups-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    tags: tags
  }
}

module monitorAlertRules 'modules/monitor-alert-rules.bicep' = {
  name: '${namePrefix}-alert-rules-module'
  scope: rg
  params: {
    namePrefix: namePrefix
    location: location
    actionGroupId: actionGroups.outputs.actionGroupId
    tags: tags
  }
}

output resourceGroupName string = rg.name
output containerRegistryLoginServer string = registry.outputs.loginServer
output backendUrl string = 'https://${backendApp.outputs.fqdn}'
output frontendUrl string = 'https://${frontendApp.outputs.fqdn}'
output keyVaultName string = keyVault.outputs.keyVaultName
output storageAccountName string = storage.outputs.storageAccountName
output cosmosDbAccountName string = cosmosDb.outputs.accountName
output aiSearchServiceName string = aiSearch.outputs.searchServiceName
output serviceBusNamespaceName string = serviceBus.outputs.namespaceName
output managedIdentityClientId string = identity.outputs.clientId
output azureOpenAIPlaceholderName string = openAiPlaceholder.outputs.accountName
