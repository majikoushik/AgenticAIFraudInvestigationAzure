"use client";

import { useCallback, useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { CaseQueueTable } from "@/components/assignment/CaseQueueTable";
import { QueueFilters } from "@/components/assignment/QueueFilters";
import type { QueueFilters as FilterValues, QueueResponse } from "@/types/assignment.types";

type Props = {
  title: string;
  subtitle: string;
  loader: (filters?: FilterValues) => Promise<QueueResponse>;
};

export function AssignmentQueuePage({ title, subtitle, loader }: Props) {
  const [filters, setFilters] = useState<FilterValues>({});
  const [queue, setQueue] = useState<QueueResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    setLoading(true);
    setError(null);
    loader(filters)
      .then(setQueue)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [filters, loader]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title={title} subtitle={subtitle} />
        <section className="content grid">
          <QueueFilters filters={filters} onChange={setFilters} />
          {loading ? <LoadingSpinner label="Loading queue" /> : error ? <ErrorMessage message={error} /> : queue && <CaseQueueTable cases={queue.cases} title={title} onRefresh={refresh} />}
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
