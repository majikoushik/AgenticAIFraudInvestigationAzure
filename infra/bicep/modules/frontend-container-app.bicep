param namePrefix string
param location string
param containerAppEnvironmentId string
param managedIdentityId string
param managedIdentityClientId string
param acrLoginServer string
param imageName string
param backendApiBaseUrl string
param tags object

resource app 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${namePrefix}-frontend-ca'
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
        targetPort: 3000
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
          name: 'frontend'
          image: imageName
          env: [
            {
              name: 'NEXT_PUBLIC_API_BASE_URL'
              value: backendApiBaseUrl
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
