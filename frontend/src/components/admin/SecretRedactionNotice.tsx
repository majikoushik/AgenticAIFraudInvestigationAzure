export function SecretRedactionNotice() {
  return (
    <div className="notice warning">
      Secret values such as API keys, tokens, passwords, connection strings, and webhooks are never displayed or edited in this panel. Use Key Vault or secure deployment variables for secrets.
    </div>
  );
}
