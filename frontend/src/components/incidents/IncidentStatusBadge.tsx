export function IncidentStatusBadge({ status }: { status: string }) {
  return <span className="badge risk-medium">{status}</span>;
}
