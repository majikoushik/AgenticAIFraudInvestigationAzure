"use client";

import { AssignmentQueuePage } from "@/components/assignment/AssignmentQueuePage";
import { getSlaRiskQueue } from "@/services/assignmentService";

export default function SlaRiskQueuePage() {
  return <AssignmentQueuePage title="SLA Risk Queue" subtitle="Cases with breached or at-risk assignment SLAs." loader={getSlaRiskQueue} />;
}
