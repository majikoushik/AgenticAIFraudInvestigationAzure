param privateEndpointsEnabled bool
param vnetId string
param tags object

var zones = [
  'privatelink.vaultcore.azure.net'
  'privatelink.blob.core.windows.net'
  'privatelink.documents.azure.com'
  'privatelink.search.windows.net'
  'privatelink.openai.azure.com'
  'privatelink.servicebus.windows.net'
  'privatelink.azurecr.io'
]

resource dnsZones 'Microsoft.Network/privateDnsZones@2020-06-01' = [for zoneName in zones: if (privateEndpointsEnabled) {
  name: zoneName
  location: 'global'
  tags: tags
}]

resource links 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = [for (zoneName, i) in zones: if (privateEndpointsEnabled) {
  parent: dnsZones[i]
  name: 'vnet-link'
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnetId
    }
  }
}]

output privateDnsZoneNames array = privateEndpointsEnabled ? zones : []
