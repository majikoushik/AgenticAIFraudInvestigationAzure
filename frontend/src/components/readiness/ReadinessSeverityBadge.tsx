"use client";

import type { ReadinessSeverity } from "@/types/readiness.types";

interface Props {
  severity: ReadinessSeverity;
}

const SEVERITY_CONFIG: Record<ReadinessSeverity, { label: string; className: string }> = {
  BLOCKER: { label: "BLOCKER", className: "severity-badge severity-badge--blocker" },
  HIGH: { label: "HIGH", className: "severity-badge severity-badge--high" },
  MEDIUM: { label: "MEDIUM", className: "severity-badge severity-badge--medium" },
  LOW: { label: "LOW", className: "severity-badge severity-badge--low" },
  INFO: { label: "INFO", className: "severity-badge severity-badge--info" },
};

export function ReadinessSeverityBadge({ severity }: Props) {
  const config = SEVERITY_CONFIG[severity] ?? {
    label: severity,
    className: "severity-badge severity-badge--info",
  };
  return <span className={config.className}>{config.label}</span>;
}
