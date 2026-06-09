"use client";

import { useEffect, useState } from "react";
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

  useEffect(() => {
    let mounted = true;
    const doLoad = async () => {
      try {
        const result = await getFeedbackBacklog();
        if (mounted) setItems(result.backlog_items);
      } catch (err: unknown) {
        if (mounted) setError(err instanceof Error ? err.message : String(err));
      } finally {
        if (mounted) setLoading(false);
      }
    };
    doLoad();
    return () => { mounted = false; };
  }, []);

  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Improvement Backlog" subtitle="Prompt, RAG, safety, and evaluation actions from feedback." />
        <section className="content">
          <FeedbackExportPanel />
          {loading ? <LoadingSpinner label="Loading backlog" /> : error ? <ErrorMessage message={error} /> : <FeedbackBacklogTable items={items} onUpdated={async () => { setLoading(true); try { const result = await getFeedbackBacklog(); setItems(result.backlog_items); } catch (err: unknown) { setError(err instanceof Error ? err.message : String(err)); } finally { setLoading(false); } }} />}
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
