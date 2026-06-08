"use client";

import { acceptCase } from "@/services/assignmentService";

type Props = {
  caseId: string;
  userId: string;
  disabled?: boolean;
  onDone: () => void;
};

export function AcceptCaseButton({ caseId, userId, disabled, onDone }: Props) {
  async function handleAccept() {
    await acceptCase(caseId, userId, "Accepted from queue.");
    onDone();
  }

  return (
    <button className="button secondary" disabled={disabled} onClick={handleAccept}>
      Accept
    </button>
  );
}
