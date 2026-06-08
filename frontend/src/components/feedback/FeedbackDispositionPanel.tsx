"use client";

import { useState } from "react";
import { updateFeedbackDisposition } from "@/services/feedbackService";
import type { FeedbackDisposition } from "@/types/feedback.types";

export function FeedbackDispositionPanel({ feedbackId, onUpdated }: { feedbackId: string; onUpdated?: () => void }) {
  const [disposition, setDisposition] = useState<FeedbackDisposition>("TRIAGED");
  async function update() {
    await updateFeedbackDisposition(feedbackId, disposition);
    onUpdated?.();
  }
  return (
    <div className="inline-actions">
      <select value={disposition} onChange={(event) => setDisposition(event.target.value as FeedbackDisposition)}>
        {["TRIAGED", "ACCEPTED_FOR_IMPROVEMENT", "REJECTED_NO_ACTION", "CONVERTED_TO_EVAL_CASE", "RESOLVED", "CLOSED"].map((item) => <option key={item} value={item}>{item}</option>)}
      </select>
      <button className="button secondary" onClick={update}>Update</button>
    </div>
  );
}
