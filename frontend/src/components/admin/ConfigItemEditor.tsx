import { useState } from "react";
import { ConfigValueInput } from "@/components/admin/ConfigValueInput";
import type { AdminConfigItem } from "@/types/adminConfig.types";

export function ConfigItemEditor({ item, onSave }: { item: AdminConfigItem; onSave: (key: string, value: unknown) => Promise<void> }) {
  const [value, setValue] = useState<unknown>(item.value);
  const [saving, setSaving] = useState(false);
  const dirty = value !== item.value;
  return (
    <div className="panel-item">
      <div className="provider-row">
        <div>
          <h4>{item.key}</h4>
          <p>{item.description}</p>
          <p className="caption">Default: {String(item.default_value)} | Source: {item.source} | Type: {item.data_type}</p>
        </div>
        <div className="badge-row">
          {!item.editable && <span className="badge status-badge">Read only</span>}
          {item.requires_restart && <span className="badge risk-medium">Restart</span>}
        </div>
      </div>
      <div className="form-grid">
        <div className="field"><label>Current value</label><ConfigValueInput item={item} value={value} onChange={setValue} /></div>
        <button className="button" disabled={!item.editable || !dirty || saving} type="button" onClick={async () => { setSaving(true); await onSave(item.key, value); setSaving(false); }}>Save</button>
      </div>
    </div>
  );
}
