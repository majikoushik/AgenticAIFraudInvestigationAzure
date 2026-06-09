"use client";

import { use, useEffect, useState } from "react";
import { getAssessment } from "@/services/readinessService";
import type { ReadinessAssessment } from "@/types/readiness.types";
import { ReadinessSummaryCards } from "@/components/readiness/ReadinessSummaryCards";
import { GoLiveDecisionBanner } from "@/components/readiness/GoLiveDecisionBanner";
import { ReadinessCategoryScoreGrid } from "@/components/readiness/ReadinessCategoryScoreGrid";
import { ReadinessChecklistTable } from "@/components/readiness/ReadinessChecklistTable";
import { ReadinessReportExporter } from "@/components/readiness/ReadinessReportExporter";
import { EvidenceSubmitForm } from "@/components/readiness/EvidenceSubmitForm";
import { useAuth } from "@/auth/useAuth";

interface Props {
  params: Promise<{ id: string }>;
}

export default function AssessmentDetailPage({ params }: Props) {
  const { id } = use(params);
  const { user } = useAuth();
  const [assessment, setAssessment] = useState<ReadinessAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"checklist" | "evidence" | "export">("checklist");

  const canEvidence = user?.role === "ADMIN" || user?.role === "COMPLIANCE_OFFICER";
  const canExport = ["ADMIN", "COMPLIANCE_OFFICER", "AUDITOR"].includes(user?.role ?? "");

  useEffect(() => {
    let mounted = true;
    const doLoad = async () => {
      try {
        const a = await getAssessment(id);
        if (mounted) setAssessment(a);
      } catch (e: unknown) {
        if (mounted) setError(e instanceof Error ? e.message : "Failed to load assessment");
      } finally {
        if (mounted) setLoading(false);
      }
    };
    doLoad();
    return () => { mounted = false; };
  }, [id]);

  async function load() {
    setLoading(true);
    try {
      const a = await getAssessment(id);
      setAssessment(a);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load assessment");
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="readiness-loading">Loading assessment...</div>;
  if (error) return <div className="readiness-error readiness-error--page">{error}</div>;
  if (!assessment) return <div className="readiness-empty">Assessment not found.</div>;

  return (
    <main className="page readiness-page" aria-label="Assessment Detail">
      <div className="page__header">
        <h1 className="page__title">Assessment Detail</h1>
        <p className="page__subtitle">
          <code>{assessment.assessment_id}</code> — {assessment.environment} — {" "}
          {new Date(assessment.created_at).toLocaleString()}
        </p>
      </div>

      <GoLiveDecisionBanner decision={assessment.go_live_decision} summary={assessment.summary} />
      <ReadinessSummaryCards assessment={assessment} />

      <section className="readiness-section">
        <h2 className="readiness-section__title">Category Scores</h2>
        <ReadinessCategoryScoreGrid categoryResults={assessment.category_results} />
      </section>

      <div className="readiness-tabs">
        <button
          id="tab-checklist"
          className={`tab-btn ${activeTab === "checklist" ? "tab-btn--active" : ""}`}
          onClick={() => setActiveTab("checklist")}
        >
          Checklist
        </button>
        {canEvidence && (
          <button
            id="tab-evidence"
            className={`tab-btn ${activeTab === "evidence" ? "tab-btn--active" : ""}`}
            onClick={() => setActiveTab("evidence")}
          >
            Add Evidence
          </button>
        )}
        {canExport && (
          <button
            id="tab-export"
            className={`tab-btn ${activeTab === "export" ? "tab-btn--active" : ""}`}
            onClick={() => setActiveTab("export")}
          >
            Export Report
          </button>
        )}
      </div>

      {activeTab === "checklist" && (
        <section className="readiness-section">
          <ReadinessChecklistTable categoryResults={assessment.category_results} />
        </section>
      )}

      {activeTab === "evidence" && canEvidence && (
        <section className="readiness-section">
          <EvidenceSubmitForm assessmentId={assessment.assessment_id} onAdded={load} />
        </section>
      )}

      {activeTab === "export" && canExport && (
        <section className="readiness-section">
          <ReadinessReportExporter assessmentId={assessment.assessment_id} />
        </section>
      )}
    </main>
  );
}
