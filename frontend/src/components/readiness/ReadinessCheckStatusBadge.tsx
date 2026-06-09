"use client";

import type { ReadinessStatus } from "@/types/readiness.types";

interface Props {
  status: ReadinessStatus;
  size?: "sm" | "md";
}

const STATUS_CONFIG: Record<ReadinessStatus, { label: string; icon: string; className: string }> = {
  PASS: { label: "Pass", icon: "✅", className: "badge badge--pass" },
  FAIL: { label: "Fail", icon: "❌", className: "badge badge--fail" },
  WARNING: { label: "Warning", icon: "⚠️", className: "badge badge--warning" },
  NOT_APPLICABLE: { label: "N/A", icon: "—", className: "badge badge--na" },
  MANUAL_REVIEW_REQUIRED: { label: "Manual Review", icon: "🔵", className: "badge badge--manual" },
  NOT_CHECKED: { label: "Not Checked", icon: "⬜", className: "badge badge--unchecked" },
};

export function ReadinessCheckStatusBadge({ status, size = "md" }: Props) {
  const config = STATUS_CONFIG[status] ?? {
    label: status,
    icon: "❓",
    className: "badge badge--unknown",
  };
  return (
    <span className={`${config.className} badge--${size}`} title={status}>
      {config.icon} {config.label}
    </span>
  );
}
