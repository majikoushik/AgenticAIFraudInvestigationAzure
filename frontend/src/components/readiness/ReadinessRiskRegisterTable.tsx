"use client";

import { useState } from "react";
import type { ReadinessRiskItem } from "@/types/readiness.types";
import { ReadinessSeverityBadge } from "./ReadinessSeverityBadge";
import { closeRisk } from "@/services/readinessService";

interface Props {
  risks: ReadinessRiskItem[];
  onRefresh?: () => void;
  canManage?: boolean;
}

const STATUS_ICON: Record<string, string> = {
  OPEN: "🔴",
  MITIGATED: "🟡",
  ACCEPTED: "🟠",
  CLOSED: "✅",
};

export function ReadinessRiskRegisterTable({ risks, onRefresh, canManage }: Props) {
  const [closing, setClosing] = useState<string | null>(null);
  const [comment, setComment] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleClose(riskId: string) {
    setClosing(null);
    setError(null);
    try {
      await closeRisk(riskId, comment || undefined);
      setComment("");
      onRefresh?.();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to close risk");
    }
  }

  if (!risks.length) {
    return <p className="readiness-empty">No risks in the register.</p>;
  }

  return (
    <div className="risk-register">
      {error && <div className="readiness-error">{error}</div>}
      <table className="readiness-table">
        <thead>
          <tr>
            <th>Risk ID</th>
            <th>Title</th>
            <th>Category</th>
            <th>Severity</th>
            <th>Status</th>
            <th>Owner</th>
            <th>Mitigation Plan</th>
            <th>Target Date</th>
            {canManage && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {risks.map((risk) => (
            <tr key={risk.risk_id} className={`risk-row risk-row--${risk.status.toLowerCase()}`}>
              <td><code>{risk.risk_id}</code></td>
              <td>{risk.title}</td>
              <td>{risk.category.replace(/_/g, " ")}</td>
              <td><ReadinessSeverityBadge severity={risk.severity} /></td>
              <td>
                {STATUS_ICON[risk.status]} {risk.status}
              </td>
              <td>{risk.owner}</td>
              <td className="risk-mitigation">{risk.mitigation_plan ?? "—"}</td>
              <td>{risk.target_date ?? "—"}</td>
              {canManage && (
                <td>
                  {risk.status !== "CLOSED" && (
                    <>
                      {closing === risk.risk_id ? (
                        <div className="risk-close-inline">
                          <input
                            type="text"
                            placeholder="Close comment (optional)"
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                            className="risk-close-comment"
                          />
                          <button
                            onClick={() => handleClose(risk.risk_id)}
                            className="btn btn--sm btn--danger"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => { setClosing(null); setComment(""); }}
                            className="btn btn--sm btn--ghost"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setClosing(risk.risk_id)}
                          className="btn btn--sm btn--outline"
                        >
                          Close Risk
                        </button>
                      )}
                    </>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
