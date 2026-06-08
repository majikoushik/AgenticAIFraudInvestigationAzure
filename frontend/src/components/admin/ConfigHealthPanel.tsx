import type { ConfigHealthResponse } from "@/types/adminConfig.types";

export function ConfigHealthPanel({ health }: { health: ConfigHealthResponse }) {
  const rows = [
    ["Admin config", health.admin_config_enabled ? "Enabled" : "Disabled"],
    ["Mode", health.mode],
    ["Local store", health.local_store_accessible ? "Accessible" : "Unavailable"],
    ["History store", health.history_store_accessible ? "Accessible" : "Unavailable"],
    ["Azure App Configuration", health.azure_app_configuration_enabled ? "Enabled" : "Disabled"],
    ["Key Vault", health.key_vault_enabled ? "Enabled" : "Disabled"],
    ["Secrets redacted", health.secret_values_redacted ? "Yes" : "No"],
    ["Editable settings", String(health.editable_config_count)],
    ["Require restart", String(health.requires_restart_count)]
  ];
  return <section className="panel"><h2>Config Health</h2><div className="stack">{rows.map(([k, v]) => <div className="row" key={k}><span>{k}</span><strong>{v}</strong></div>)}</div></section>;
}
