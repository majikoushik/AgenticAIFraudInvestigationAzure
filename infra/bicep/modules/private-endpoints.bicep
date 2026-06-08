param privateEndpointsEnabled bool
param location string
param subnetId string
param keyVaultResourceId string = ''
param storageAccountResourceId string = ''
param cosmosDbResourceId string = ''
param aiSearchResourceId string = ''
param azureOpenAiResourceId string = ''
param serviceBusResourceId string = ''
param tags object

// MVP scaffold: enable this module after VNet/subnet IDs and private DNS zone groups are wired.
// Group IDs commonly used:
// Key Vault: vault, Storage: blob, Cosmos DB: Sql, Search: searchService,
// Azure OpenAI/Cognitive Services: account, Service Bus: namespace.

output privateEndpointsEnabledOutput bool = privateEndpointsEnabled
output privateEndpointResourceIds array = []
