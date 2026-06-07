export function AlertSeverityBadge({ severity }: { severity: string }) {
  const className = severity.includes("SEV0") || severity.includes("SEV1") ? "badge risk-high" : severity.includes("SEV2") ? "badge risk-medium" : "badge risk-low";
  return <span className={className}>{severity}</span>;
}
