# Managed Identity Auth Failure

Confirm the Container App has the user-assigned identity, `AZURE_CLIENT_ID` matches the identity client ID, and the identity has resource RBAC. Fall back to local development credentials only outside production.
