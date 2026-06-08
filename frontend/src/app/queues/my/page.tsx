"use client";

import { AssignmentQueuePage } from "@/components/assignment/AssignmentQueuePage";
import { getMyQueue } from "@/services/assignmentService";

export default function MyQueuePage() {
  return <AssignmentQueuePage title="My Queue" subtitle="Cases assigned to the signed-in investigator." loader={getMyQueue} />;
}
