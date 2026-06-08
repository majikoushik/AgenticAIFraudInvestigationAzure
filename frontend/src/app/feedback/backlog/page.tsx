"use client";

import { useCallback, useEffect, useState } from "react";
import { Header } from "@/components/common/Header";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { FeedbackBacklogTable } from "@/components/feedback/FeedbackBacklogTable";
import { FeedbackExportPanel } from "@/components/feedback/FeedbackExportPanel";
import { getFeedbackBacklog } from "@/services/feedbackService";
import type { FeedbackBacklogItem } from "@/types/feedback.types";

export default function FeedbackBacklogPage() {
  const [items, setItems] = useState<FeedbackBacklogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    getFeedbackBacklog().then((result) => setItems(result.backlog_items)).catch((err: Error) => setError(err.message)).finally(() => setLoading(false));
  }, []);

  useEffect(() => load(), [load]);

  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Improvement Backlog" subtitle="Prompt, RAG, safety, and evaluation actions from feedback." />
        <section className="content">
          <FeedbackExportPanel />
          {loading ? <LoadingSpinner label="Loading backlog" /> : error ? <ErrorMessage message={error} /> : <FeedbackBacklogTable items={items} onUpdated={load} />}
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
