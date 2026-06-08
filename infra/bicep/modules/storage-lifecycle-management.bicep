param storageAccountName string
param enableLifecycleRules bool = false

// Placeholder only. Production lifecycle policies should be reviewed by legal
// and compliance before moving exports to cool/archive or applying immutable
// retention/legal hold controls.
resource lifecycle 'Microsoft.Storage/storageAccounts/managementPolicies@2023-05-01' = if (enableLifecycleRules) {
  name: '${storageAccountName}/default'
  properties: {
    policy: {
      rules: [
        {
          enabled: false
          name: 'archive-compliance-exports-placeholder'
          type: 'Lifecycle'
          definition: {
            filters: {
              blobTypes: [
                'blockBlob'
              ]
              prefixMatch: [
                'compliance-exports/'
                'archives/'
                'retention-reports/'
              ]
            }
            actions: {
              baseBlob: {
                tierToCool: {
                  daysAfterModificationGreaterThan: 90
                }
                tierToArchive: {
                  daysAfterModificationGreaterThan: 365
                }
              }
            }
          }
        }
      ]
    }
  }
}

output lifecycleRulesEnabled bool = enableLifecycleRules
