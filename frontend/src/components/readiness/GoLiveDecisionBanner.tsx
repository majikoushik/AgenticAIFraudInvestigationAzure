"use client";

import type { GoLiveDecision } from "@/types/readiness.types";

interface Props {
  decision: GoLiveDecision | null;
  summary?: string;
}

const DECISION_CONFIG: Record<GoLiveDecision, { label: string; icon: string; className: string }> = {
  READY: {
    label: "✅ READY FOR PRODUCTION",
    icon: "✅",
    className: "go-live-banner go-live-banner--ready",
  },
  READY_WITH_RISKS: {
    label: "⚠️ READY WITH RISKS — Review risk register before deploying",
    icon: "⚠️",
    className: "go-live-banner go-live-banner--risks",
  },
  NOT_READY: {
    label: "❌ NOT READY — Blocking issues must be resolved",
    icon: "❌",
    className: "go-live-banner go-live-banner--not-ready",
  },
  MANUAL_REVIEW_REQUIRED: {
    label: "🔵 MANUAL REVIEW REQUIRED — Evidence pending",
    icon: "🔵",
    className: "go-live-banner go-live-banner--manual",
  },
};

export function GoLiveDecisionBanner({ decision, summary }: Props) {
  if (!decision) {
    return (
      <div className="go-live-banner go-live-banner--empty">
        <span>No assessment available. Run an assessment to see go-live status.</span>
      </div>
    );
  }

  const config = DECISION_CONFIG[decision];
  return (
    <div className={config.className} role="status" aria-label={`Go-live decision: ${decision}`}>
      <div className="go-live-banner__label">{config.label}</div>
      {summary && <div className="go-live-banner__summary">{summary}</div>}
    </div>
  );
}
