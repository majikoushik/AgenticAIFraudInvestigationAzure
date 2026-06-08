# Pipelines

Azure DevOps YAML uses placeholder service connections and variable group names. Secret values must come from Azure Key Vault-backed variable groups or authorized manual setup, never from YAML.

Security validation stages run no-secret scans, Bicep validation/what-if placeholders, and post-deployment security check placeholders.
