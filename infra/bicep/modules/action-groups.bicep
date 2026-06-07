param namePrefix string
param location string
param tags object

// Placeholder action group. Add email/webhook/Teams receivers through secure parameters or Key Vault references.
resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: '${namePrefix}-ops-ag'
  location: 'Global'
  tags: tags
  properties: {
    groupShortName: 'fraudops'
    enabled: true
    emailReceivers: []
    webhookReceivers: []
  }
}

output actionGroupId string = actionGroup.id
