"use client";

import { useState } from "react";
import { runAssessment } from "@/services/readinessService";
import type { ReadinessAssessment, RunAssessmentPayload } from "@/types/readiness.types";

interface Props {
  onComplete?: (assessment: ReadinessAssessment) => void;
  disabled?: boolean;
}

const ENVIRONMENTS = ["prod", "staging", "dev", "local"];

export function RunAssessmentPanel({ onComplete, disabled }: Props) {
  const [environment, setEnvironment] = useState("prod");
  const [createRisks, setCreateRisks] = useState(true);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    setLoading(true);
    setError(null);
    try {
      const payload: RunAssessmentPayload = {
        environment,
        categories: null,
        create_risks_from_failures: createRisks,
        comment: comment || undefined,
      };
      const result = await runAssessment(payload);
      onComplete?.(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Assessment failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="run-assessment-panel">
      <h3 className="run-assessment-panel__title">Run Production Readiness Assessment</h3>
      <p className="run-assessment-panel__subtitle">
        Executes all 120+ automated and heuristic checks across 20 readiness categories.
      </p>

      {error && <div className="readiness-error">{error}</div>}

      <div className="run-assessment-panel__form">
        <div className="form-group">
          <label htmlFor="ra-environment" className="form-label">
            Target Environment
          </label>
          <select
            id="ra-environment"
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
            className="form-select"
            disabled={loading || disabled}
          >
            {ENVIRONMENTS.map((env) => (
              <option key={env} value={env}>
                {env}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group form-group--checkbox">
          <label className="form-checkbox">
            <input
              id="ra-create-risks"
              type="checkbox"
              checked={createRisks}
              onChange={(e) => setCreateRisks(e.target.checked)}
              disabled={loading || disabled}
            />
            <span>Auto-create risks from failed BLOCKER/HIGH checks</span>
          </label>
        </div>

        <div className="form-group">
          <label htmlFor="ra-comment" className="form-label">
            Comment (optional)
          </label>
          <input
            id="ra-comment"
            type="text"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            className="form-input"
            placeholder="Pre-release assessment, Q2 review..."
            disabled={loading || disabled}
          />
        </div>

        <button
          id="btn-run-readiness-assessment"
          onClick={handleRun}
          disabled={loading || disabled}
          className="btn btn--primary btn--run-assessment"
        >
          {loading ? "⏳ Running Assessment..." : "▶ Run Assessment"}
        </button>
      </div>

      {disabled && (
        <div className="run-assessment-panel__permission-notice">
          ℹ️ Running assessments requires the <strong>ADMIN</strong> role.
        </div>
      )}
    </div>
  );
}
