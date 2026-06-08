"use client";

import { useEffect, useState } from "react";
import { getRetentionReviewQueue } from "@/services/retentionService";
import { RetentionScanResultTable } from "@/components/compliance/RetentionScanResultTable";
import type { RetentionCandidate } from "@/types/retention.types";

export function RetentionReviewQueue() {
  const [candidates, setCandidates] = useState<RetentionCandidate[]>([]);
  useEffect(() => { getRetentionReviewQueue().then((response) => setCandidates(response.candidates)).catch(() => setCandidates([])); }, []);
  return <RetentionScanResultTable candidates={candidates} />;
}
