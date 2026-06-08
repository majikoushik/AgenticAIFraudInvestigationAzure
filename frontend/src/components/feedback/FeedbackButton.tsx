"use client";

import { useState } from "react";
import { FeedbackModal } from "@/components/feedback/FeedbackModal";
import type { FeedbackTargetType } from "@/types/feedback.types";

type Props = {
  caseId: string;
  targetType: FeedbackTargetType;
  label?: string;
  actualAiRecommendation?: string | null;
  humanDecision?: string | null;
  agentName?: string | null;
  policySourceFile?: string | null;
  policyChunkId?: string | null;
  snapshot?: Record<string, unknown>;
  onSubmitted?: () => void;
};

export function FeedbackButton({ label = "Feedback", ...props }: Props) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button className="button secondary feedback-button" onClick={() => setOpen(true)}>{label}</button>
      {open && <FeedbackModal {...props} onClose={() => setOpen(false)} />}
    </>
  );
}
