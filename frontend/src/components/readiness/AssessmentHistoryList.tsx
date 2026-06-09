"use client";

import type { ReadinessAssessment } from "@/types/readiness.types";

interface Props {
  assessments: ReadinessAssessment[];
  onSelect?: (assessment: ReadinessAssessment) => void;
  selectedId?: string;
}

export function AssessmentHistoryList({ assessments, onSelect, selectedId }: Props) {
  if (!assessments.length) {
    return <p className="readiness-empty">No assessment history yet.</p>;
  }

  return (
    <div className="assessment-history">
      {assessments.map((a) => (
        <div
          key={a.assessment_id}
          className={`assessment-history__item ${selectedId === a.assessment_id ? "assessment-history__item--selected" : ""}`}
          onClick={() => onSelect?.(a)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && onSelect?.(a)}
        >
          <div className="assessment-history__meta">
            <span className="assessment-history__id">
              {a.assessment_id}
            </span>
            <span className="assessment-history__env">
              {a.environment}
            </span>
            <span className={`assessment-history__decision assessment-history__decision--${a.go_live_decision.toLowerCase().replace(/_/g, "-")}`}>
              {a.go_live_decision.replace(/_/g, " ")}
            </span>
          </div>
          <div className="assessment-history__stats">
            <span>Score: <strong>{a.overall_score.toFixed(1)}</strong></span>
            <span>Blockers: <strong>{a.blocking_issue_count}</strong></span>
            <span>By: {a.created_by}</span>
            <span>{new Date(a.created_at).toLocaleString()}</span>
          </div>
          {a.summary && (
            <div className="assessment-history__summary">{a.summary}</div>
          )}
        </div>
      ))}
    </div>
  );
}
