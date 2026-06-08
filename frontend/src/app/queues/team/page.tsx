"use client";

import { AssignmentQueuePage } from "@/components/assignment/AssignmentQueuePage";
import { getTeamQueue } from "@/services/assignmentService";

export default function TeamQueuePage() {
  return <AssignmentQueuePage title="Team Queue" subtitle="Manager and auditor view of team case ownership." loader={getTeamQueue} />;
}
