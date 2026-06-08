import type { ComplianceExport } from "@/types/compliance.types";

export function ComplianceExportList({ exports }: { exports: ComplianceExport[] }) {
  return <div className="table-wrap"><table><thead><tr><th>Export</th><th>Case</th><th>Status</th><th>Redacted</th><th>Path</th></tr></thead><tbody>{exports.map((item) => <tr key={item.export_id}><td>{item.export_id}</td><td>{item.case_id}</td><td>{item.status}</td><td>{String(item.manifest?.redaction_applied ?? true)}</td><td>{item.output_path ?? "-"}</td></tr>)}</tbody></table></div>;
}
