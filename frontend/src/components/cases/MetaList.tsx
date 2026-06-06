type MetaListProps = {
  rows: Array<{ label: string; value: string | number | boolean | null | undefined }>;
};

export function MetaList({ rows }: MetaListProps) {
  return (
    <div className="meta-list">
      {rows.map((row) => (
        <div className="meta-row" key={row.label}>
          <span className="meta-label">{row.label}</span>
          <span className="meta-value">{formatValue(row.value)}</span>
        </div>
      ))}
    </div>
  );
}

function formatValue(value: string | number | boolean | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "Not available";
  }
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }
  return String(value);
}
