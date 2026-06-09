"use client";

import { useEffect, useState } from "react";
import { listAssessments } from "@/services/readinessService";
import type { ReadinessAssessment } from "@/types/readiness.types";
import { ReadinessSummaryCards } from "@/components/readiness/ReadinessSummaryCards";
import { GoLiveDecisionBanner } from "@/components/readiness/GoLiveDecisionBanner";
import { ReadinessCategoryScoreGrid } from "@/components/readiness/ReadinessCategoryScoreGrid";
import { RunAssessmentPanel } from "@/components/readiness/RunAssessmentPanel";
import { AssessmentHistoryList } from "@/components/readiness/AssessmentHistoryList";
import { useAuth } from "@/auth/useAuth";

export default function ReadinessDashboardPage() {
  const { user } = useAuth();
  const [assessments, setAssessments] = useState<ReadinessAssessment[]>([]);
  const [selected, setSelected] = useState<ReadinessAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAdmin = user?.role === "ADMIN";

  useEffect(() => {
    let mounted = true;
    const doLoad = async () => {
      try {
        const result = await listAssessments({ limit: 20 });
        if (mounted) {
          setAssessments(result.assessments);
          setSelected((prevSelected) => prevSelected || (result.assessments.length > 0 ? result.assessments[0] : null));
        }
      } catch (e: unknown) {
        if (mounted) setError(e instanceof Error ? e.message : "Failed to load assessments");
      } finally {
        if (mounted) setLoading(false);
      }
    };
    doLoad();
    return () => { mounted = false; };
  }, []);

  function handleNewAssessment(assessment: ReadinessAssessment) {
    setAssessments((prev) => [assessment, ...prev]);
    setSelected(assessment);
  }

  return (
    <main className="page readiness-page" aria-label="Production Readiness Dashboard">
      <div className="page__header">
        <h1 className="page__title">Production Readiness Dashboard</h1>
        <p className="page__subtitle">
          End-to-end production readiness framework across 20 categories and 120+ checks.
        </p>
      </div>

      {error && <div className="readiness-error readiness-error--page">{error}</div>}

      {/* Go-live decision banner */}
      <GoLiveDecisionBanner
        decision={selected?.go_live_decision ?? null}
        summary={selected?.summary}
      />

      {/* Summary cards */}
      <ReadinessSummaryCards assessment={selected} loading={loading} />

      {/* Category score grid */}
      {selected && (
        <section className="readiness-section">
          <h2 className="readiness-section__title">Category Scores</h2>
          <ReadinessCategoryScoreGrid categoryResults={selected.category_results} />
        </section>
      )}

      <div className="readiness-main-grid">
        {/* Run assessment */}
        {isAdmin && (
          <section className="readiness-section readiness-section--panel">
            <RunAssessmentPanel onComplete={handleNewAssessment} disabled={!isAdmin} />
          </section>
        )}
        {!isAdmin && (
          <div className="readiness-section readiness-section--panel">
            <RunAssessmentPanel onComplete={handleNewAssessment} disabled={true} />
          </div>
        )}

        {/* History */}
        <section className="readiness-section readiness-section--history">
          <h2 className="readiness-section__title">Assessment History</h2>
          <AssessmentHistoryList
            assessments={assessments}
            selectedId={selected?.assessment_id}
            onSelect={setSelected}
          />
        </section>
      </div>
    </main>
  );
}
