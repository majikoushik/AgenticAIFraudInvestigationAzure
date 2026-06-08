"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/common/Header";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { FeedbackList } from "@/components/feedback/FeedbackList";
import { FeedbackSettingsNote } from "@/components/feedback/FeedbackSettingsNote";
import { getFeedback } from "@/services/feedbackService";
import type { FeedbackRecord } from "@/types/feedback.types";

export default function FeedbackDashboardPage() {
  const [records, setRecords] = useState<FeedbackRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getFeedback()
      .then((result) => setRecords(result.feedback_records))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="AI Feedback" subtitle="Investigator feedback on AI outputs and RAG quality." />
        <section className="content">
          <FeedbackSettingsNote />
          {loading ? <LoadingSpinner label="Loading feedback" /> : error ? <ErrorMessage message={error} /> : <FeedbackList records={records} />}
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
