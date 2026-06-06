"use client";

import { useEffect, useMemo, useState } from "react";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { CaseStatsCard } from "@/components/dashboard/CaseStatsCard";
import { RecentCasesTable } from "@/components/dashboard/RecentCasesTable";
import { getCaseSummaries } from "@/services/caseService";
import type { CaseSummary } from "@/types/case.types";

export default function DashboardPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCaseSummaries()
      .then(setCases)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const stats = useMemo(() => {
    const highRisk = cases.filter((item) => ["high", "critical"].includes(item.severity.toLowerCase())).length;
    const pending = cases.filter((item) => item.status.includes("review") || item.status === "triage").length;
    const escalated = cases.filter((item) => item.status.includes("escalated")).length;
    const completed = cases.filter((item) => item.status.includes("complete") || item.status.includes("closed")).length;
    return { highRisk, pending, escalated, completed };
  }, [cases]);

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Fraud Investigation Dashboard" subtitle="Operational view of synthetic fraud alerts and investigation workload." />
        <section className="content">
          {loading ? (
            <LoadingSpinner label="Loading dashboard metrics" />
          ) : error ? (
            <ErrorMessage message={error} />
          ) : (
            <div className="grid">
              <div className="stats-grid grid">
                <CaseStatsCard label="Total cases" value={cases.length} />
                <CaseStatsCard label="High-risk cases" value={stats.highRisk} tone="high" />
                <CaseStatsCard label="Pending review" value={stats.pending} tone="medium" />
                <CaseStatsCard label="Escalated cases" value={stats.escalated} />
                <CaseStatsCard label="Completed cases" value={stats.completed} />
              </div>
              <RecentCasesTable cases={cases.slice(0, 8)} />
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
