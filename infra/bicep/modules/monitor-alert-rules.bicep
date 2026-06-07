param namePrefix string
param location string
param actionGroupId string
param tags object

// Placeholder module for Azure Monitor scheduled query alert rules.
// Wire Log Analytics workspace IDs and KQL from monitoring/kql/*.kql in production deployment pipelines.
resource placeholder 'Microsoft.Resources/tags@2021-04-01' = {
  name: 'default'
  properties: {
    tags: union(tags, {
      monitorAlertRulesPlaceholder: '${namePrefix}-${location}'
      actionGroupId: actionGroupId
    })
  }
}
