export function AlertTypeBadge({ alertType }: { alertType: string }) {
  return <span className="badge">{alertType.replaceAll("_", " ")}</span>;
}
