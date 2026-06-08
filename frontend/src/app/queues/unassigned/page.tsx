"use client";

import { AssignmentQueuePage } from "@/components/assignment/AssignmentQueuePage";
import { getUnassignedQueue } from "@/services/assignmentService";

export default function UnassignedQueuePage() {
  return <AssignmentQueuePage title="Unassigned Queue" subtitle="Cases available for assignment or self-assignment." loader={getUnassignedQueue} />;
}
