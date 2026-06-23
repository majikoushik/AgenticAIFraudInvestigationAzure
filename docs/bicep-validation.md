# Bicep Validation Guidance

To validate the Azure Bicep templates locally without deploying them to a live subscription, use the Azure CLI `bicep build` command. This ensures the syntax and structure are correct.

## Prerequisites

- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) must be installed.
- Bicep CLI should be installed (it is often included with newer versions of Azure CLI, or can be installed via `az bicep install`).

## Validation Command

Run the following command from the root of the repository:

```bash
az bicep build --file infra/bicep/main.bicep
```

This command will output warnings or errors if the Bicep code is invalid, and will generate an ARM template (`main.json`) in the same directory. Note that this validation does not check if the resources actually exist in your subscription or if your subscription quota limits are reached.

The CI/CD pipeline (`pipelines/azure-pipelines.yml`) includes an automated validation step (`az deployment sub validate`) which connects to Azure to perform a deeper pre-flight validation.
