param(
    [string]$Location = "eastus",
    [string]$DeploymentName = "fraud-ai-dev-deploy"
)

# Deploy the dev MVP infrastructure.
# Assumes `az login` and the correct subscription are already selected.
az deployment sub create `
    --name $DeploymentName `
    --location $Location `
    --template-file infra/bicep/main.bicep `
    --parameters "@infra/bicep/parameters/dev.parameters.json"
