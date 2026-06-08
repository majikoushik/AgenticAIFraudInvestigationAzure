"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { InvestigatorWorkloadTable } from "@/components/assignment/InvestigatorWorkloadTable";
import { WorkloadSummaryCards } from "@/components/assignment/WorkloadSummaryCards";
import { getWorkloadSummary } from "@/services/assignmentService";
import type { WorkloadSummary } from "@/types/assignment.types";

export default function WorkloadPage() {
  const [summary, setSummary] = useState<WorkloadSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getWorkloadSummary().then(setSummary).catch((err: Error) => setError(err.message));
  }, []);

  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Assignment Workload" subtitle="Team workload and SLA pressure from local synthetic cases." />
        <section className="content grid">
          {error ? <ErrorMessage message={error} /> : !summary ? <LoadingSpinner label="Loading workload" /> : (
            <>
              <WorkloadSummaryCards summary={summary} />
              <InvestigatorWorkloadTable investigators={[...summary.available_investigators, ...summary.overloaded_investigators]} />
            </>
          )}
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
