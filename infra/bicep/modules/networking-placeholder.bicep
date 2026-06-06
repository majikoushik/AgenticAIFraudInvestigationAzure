param namePrefix string
param location string
param tags object

resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: '${namePrefix}-vnet'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.40.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'container-apps-placeholder'
        properties: {
          addressPrefix: '10.40.1.0/24'
          delegations: [
            {
              name: 'container-apps-delegation'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
      {
        name: 'private-endpoints-placeholder'
        properties: {
          addressPrefix: '10.40.2.0/24'
        }
      }
    ]
  }
}

// The Container Apps environment is not attached to this VNet in the MVP.
// Wire this VNet into the environment module when private networking is required.

output vnetName string = vnet.name
output vnetResourceId string = vnet.id
