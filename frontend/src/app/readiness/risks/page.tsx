"use client";

import { useEffect, useState } from "react";
import { listRisks } from "@/services/readinessService";
import type { ReadinessRiskItem } from "@/types/readiness.types";
import { ReadinessRiskRegisterTable } from "@/components/readiness/ReadinessRiskRegisterTable";
import { CreateRiskForm } from "@/components/readiness/CreateRiskForm";
import { useAuth } from "@/auth/useAuth";

export default function ReadinessRisksPage() {
  const { user } = useAuth();
  const [risks, setRisks] = useState<ReadinessRiskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("OPEN");
  const [showCreate, setShowCreate] = useState(false);

  const canManage = user?.role === "ADMIN" || user?.role === "COMPLIANCE_OFFICER";

  useEffect(() => {
    let mounted = true;
    const doLoad = async () => {
      try {
        const result = await listRisks({ status: statusFilter === "ALL" ? undefined : statusFilter });
        if (mounted) setRisks(result.risks);
      } catch (e: unknown) {
        if (mounted) setError(e instanceof Error ? e.message : "Failed to load risks");
      } finally {
        if (mounted) setLoading(false);
      }
    };
    doLoad();
    return () => { mounted = false; };
  }, [statusFilter]);

  async function loadRisks() {
    setLoading(true);
    setError(null);
    try {
      const result = await listRisks({ status: statusFilter === "ALL" ? undefined : statusFilter });
      setRisks(result.risks);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load risks");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page readiness-page" aria-label="Risk Register">
      <div className="page__header">
        <h1 className="page__title">Go-Live Risk Register</h1>
        <p className="page__subtitle">
          Tracks all production readiness risks identified during assessments.
        </p>
        {canManage && (
          <button
            id="btn-show-create-risk"
            className="btn btn--primary"
            onClick={() => setShowCreate((v) => !v)}
          >
            {showCreate ? "Hide Form" : "+ Create Risk"}
          </button>
        )}
      </div>

      {error && <div className="readiness-error">{error}</div>}

      {showCreate && canManage && (
        <section className="readiness-section">
          <CreateRiskForm onCreated={() => { setShowCreate(false); loadRisks(); }} />
        </section>
      )}

      <div className="readiness-controls">
        <label htmlFor="risk-status-filter" className="form-label">Status Filter:</label>
        <select
          id="risk-status-filter"
          className="form-select form-select--sm"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="ALL">All</option>
          <option value="OPEN">Open</option>
          <option value="MITIGATED">Mitigated</option>
          <option value="ACCEPTED">Accepted</option>
          <option value="CLOSED">Closed</option>
        </select>
        <span className="readiness-count">{risks.length} risks</span>
      </div>

      {loading ? (
        <div className="readiness-loading">Loading risks...</div>
      ) : (
        <ReadinessRiskRegisterTable
          risks={risks}
          onRefresh={loadRisks}
          canManage={canManage}
        />
      )}
    </main>
  );
}
