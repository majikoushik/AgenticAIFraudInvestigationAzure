import type { AdminConfigItem } from "@/types/adminConfig.types";

export function ConfigValueInput({ item, value, onChange }: { item: AdminConfigItem; value: unknown; onChange: (value: unknown) => void }) {
  if (item.data_type === "boolean") {
    return <input checked={Boolean(value)} disabled={!item.editable} onChange={(event) => onChange(event.target.checked)} type="checkbox" />;
  }
  if (item.data_type === "enum" && item.allowed_values) {
    return <select disabled={!item.editable} value={String(value ?? "")} onChange={(event) => onChange(event.target.value)}>{item.allowed_values.map((option) => <option key={String(option)} value={String(option)}>{String(option)}</option>)}</select>;
  }
  if (item.data_type === "integer" || item.data_type === "float") {
    return <input disabled={!item.editable} min={item.min_value ?? undefined} max={item.max_value ?? undefined} step={item.data_type === "float" ? "0.01" : "1"} type="number" value={String(value ?? "")} onChange={(event) => onChange(item.data_type === "integer" ? Number.parseInt(event.target.value, 10) : Number.parseFloat(event.target.value))} />;
  }
  return <input disabled={!item.editable} value={String(value ?? "")} onChange={(event) => onChange(event.target.value)} />;
}
