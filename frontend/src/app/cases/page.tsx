"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { CaseList } from "@/components/cases/CaseList";
import { getCaseRows } from "@/services/caseService";
import type { CaseListRow } from "@/types/case.types";

export default function CasesPage() {
  const [cases, setCases] = useState<CaseListRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCaseRows()
      .then(setCases)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Fraud Cases" subtitle="Review synthetic alerts, risk levels, and investigation status." />
        <section className="content">
          {loading ? (
            <LoadingSpinner label="Loading fraud cases" />
          ) : error ? (
            <ErrorMessage message={error} />
          ) : (
            <CaseList cases={cases} />
          )}
        </section>
      </main>
    </div>
  );
}
