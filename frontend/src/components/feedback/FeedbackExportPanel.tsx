"use client";

import { useState } from "react";
import { exportFeedbackEvalDataset } from "@/services/feedbackService";

export function FeedbackExportPanel() {
  const [message, setMessage] = useState<string | null>(null);
  async function runExport() {
    const result = await exportFeedbackEvalDataset();
    setMessage(`Exported ${result.exported_count} records to ${result.target_path}`);
  }
  return (
    <section className="card">
      <div className="card-header"><h3>Evaluation Dataset Export</h3><p>Accepted feedback only, sanitized for local eval datasets.</p></div>
      <div className="card-body">
        <button className="button" onClick={runExport}>Export Accepted Feedback</button>
        {message && <p className="success-inline">{message}</p>}
      </div>
    </section>
  );
}
