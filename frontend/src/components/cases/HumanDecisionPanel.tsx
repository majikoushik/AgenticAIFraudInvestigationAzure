"use client";

import { FormEvent, useState } from "react";
import { CardFrame } from "@/components/cases/CardFrame";
import { submitDecision } from "@/services/auditService";
import type { DecisionValue } from "@/types/decision.types";

type HumanDecisionPanelProps = {
  caseId: string;
  onDecisionRecorded: () => Promise<void>;
};

export function HumanDecisionPanel({ caseId, onDecisionRecorded }: HumanDecisionPanelProps) {
  const [decision, setDecision] = useState<DecisionValue>("hold");
  const [comment, setComment] = useState("");
  const [reviewedBy, setReviewedBy] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setMessage(null);
    setError(null);

    try {
      const response = await submitDecision(caseId, {
        decision,
        comment,
        reviewed_by: reviewedBy
      });
      setMessage(response.message);
      setComment("");
      await onDecisionRecorded();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <CardFrame title="Human Decision Panel" subtitle="Human review is required for high-impact outcomes.">
      <form className="form-grid" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="decision">Decision</label>
          <select id="decision" value={decision} onChange={(event) => setDecision(event.target.value as DecisionValue)}>
            <option value="approve">Approve</option>
            <option value="hold">Hold</option>
            <option value="escalate">Escalate</option>
            <option value="reject">Reject</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="reviewed_by">Reviewed by</label>
          <input id="reviewed_by" value={reviewedBy} onChange={(event) => setReviewedBy(event.target.value)} placeholder="synthetic.reviewer" required />
        </div>
        <div className="field">
          <label htmlFor="comment">Comment</label>
          <textarea id="comment" value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Add review rationale" required />
        </div>
        {message && <div className="message success">{message}</div>}
        {error && <div className="message error">{error}</div>}
        <button className="button" type="submit" disabled={submitting || !caseId}>
          {submitting ? "Submitting Decision" : "Submit Decision"}
        </button>
      </form>
    </CardFrame>
  );
}
