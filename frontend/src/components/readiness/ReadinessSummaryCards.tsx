"use client";

import type { ReadinessAssessment } from "@/types/readiness.types";

interface Props {
  assessment: ReadinessAssessment | null;
  loading?: boolean;
}

export function ReadinessSummaryCards({ assessment, loading }: Props) {
  if (loading) {
    return (
      <div className="readiness-summary-cards">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="readiness-card readiness-card--loading">
            <div className="readiness-card__value">--</div>
            <div className="readiness-card__label">Loading...</div>
          </div>
        ))}
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="readiness-summary-cards">
        <div className="readiness-card readiness-card--empty">
          <div className="readiness-card__value">—</div>
          <div className="readiness-card__label">No assessment yet</div>
        </div>
      </div>
    );
  }

  const cards = [
    {
      label: "Overall Score",
      value: `${assessment.overall_score.toFixed(1)}`,
      unit: "/ 100",
      color: assessment.overall_score >= 90 ? "green" : assessment.overall_score >= 70 ? "yellow" : "red",
    },
    {
      label: "Go-Live Decision",
      value: assessment.go_live_decision.replace(/_/g, " "),
      color:
        assessment.go_live_decision === "READY"
          ? "green"
          : assessment.go_live_decision === "READY_WITH_RISKS"
          ? "yellow"
          : assessment.go_live_decision === "MANUAL_REVIEW_REQUIRED"
          ? "blue"
          : "red",
    },
    {
      label: "Blocking Issues",
      value: String(assessment.blocking_issue_count),
      color: assessment.blocking_issue_count === 0 ? "green" : "red",
    },
    {
      label: "High Risk Items",
      value: String(assessment.high_risk_count),
      color: assessment.high_risk_count === 0 ? "green" : assessment.high_risk_count <= 3 ? "yellow" : "red",
    },
    {
      label: "Manual Review",
      value: String(assessment.manual_review_required_count),
      color: "blue",
    },
    {
      label: "Last Assessed",
      value: new Date(assessment.created_at).toLocaleDateString(),
      color: "neutral",
    },
  ];

  return (
    <div className="readiness-summary-cards">
      {cards.map((card) => (
        <div key={card.label} className={`readiness-card readiness-card--${card.color}`}>
          <div className="readiness-card__value">
            {card.value}
            {card.unit && <span className="readiness-card__unit"> {card.unit}</span>}
          </div>
          <div className="readiness-card__label">{card.label}</div>
        </div>
      ))}
    </div>
  );
}
