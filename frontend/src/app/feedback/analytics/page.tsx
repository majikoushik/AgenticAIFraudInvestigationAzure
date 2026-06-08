"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/common/Header";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { FeedbackAnalyticsCards } from "@/components/feedback/FeedbackAnalyticsCards";
import { FeedbackByAgentTable } from "@/components/feedback/FeedbackByAgentTable";
import { FeedbackTrendPanel } from "@/components/feedback/FeedbackTrendPanel";
import { getFeedbackAnalytics } from "@/services/feedbackService";
import type { FeedbackAnalyticsResponse } from "@/types/feedback.types";

export default function FeedbackAnalyticsPage() {
  const [analytics, setAnalytics] = useState<FeedbackAnalyticsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getFeedbackAnalytics().then(setAnalytics).catch((err: Error) => setError(err.message));
  }, []);

  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Feedback Analytics" subtitle="AI quality signals from investigator feedback." />
        <section className="content">
          {error ? <ErrorMessage message={error} /> : !analytics ? <LoadingSpinner label="Loading analytics" /> : (
            <div className="grid">
              <div className="full-span"><FeedbackAnalyticsCards analytics={analytics} /></div>
              <FeedbackTrendPanel analytics={analytics} />
              <FeedbackByAgentTable analytics={analytics} />
              <section className="card">
                <div className="card-header"><h3>Issue Types</h3><p>RAG, prompt, safety, and explanation issues.</p></div>
                <div className="card-body">
                  <table className="data-table"><tbody>{Object.entries(analytics.by_issue_type).map(([key, value]) => <tr key={key}><td>{key}</td><td>{value}</td></tr>)}</tbody></table>
                </div>
              </section>
              <section className="card">
                <div className="card-header"><h3>Target Types</h3><p>Where feedback is being submitted.</p></div>
                <div className="card-body">
                  <table className="data-table"><tbody>{Object.entries(analytics.by_target_type).map(([key, value]) => <tr key={key}><td>{key}</td><td>{value}</td></tr>)}</tbody></table>
                </div>
              </section>
            </div>
          )}
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
