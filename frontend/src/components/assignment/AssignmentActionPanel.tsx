"use client";

import { useAuth } from "@/auth/useAuth";
import { AcceptCaseButton } from "@/components/assignment/AcceptCaseButton";
import { AssignCaseModal } from "@/components/assignment/AssignCaseModal";
import { ReassignCaseModal } from "@/components/assignment/ReassignCaseModal";
import { ReleaseCaseModal } from "@/components/assignment/ReleaseCaseModal";
import type { CaseAssignment } from "@/types/assignment.types";

type Props = {
  caseId: string;
  assignment: CaseAssignment | null | undefined;
  onDone: () => void;
};

export function AssignmentActionPanel({ caseId, assignment, onDone }: Props) {
  const { user, hasPermission } = useAuth();
  if (!user) return null;
  const canManage = hasPermission("ASSIGN_CASE") || hasPermission("REASSIGN_CASE");
  const canReleaseOwn = hasPermission("RELEASE_CASE") && assignment?.assigned_to === user.user_id;

  return (
    <section className="card">
      <div className="card-header">
        <h3>Assignment Actions</h3>
        <p>Available actions are still validated by the backend.</p>
      </div>
      <div className="card-body panel-list">
        {hasPermission("ACCEPT_CASE") && (
          <div className="panel-item">
            <h4>Accept Case</h4>
            <AcceptCaseButton caseId={caseId} userId={user.user_id} disabled={Boolean(assignment?.assigned_to && assignment.assigned_to !== user.user_id && !canManage)} onDone={onDone} />
          </div>
        )}
        {canManage && <AssignCaseModal caseId={caseId} onDone={onDone} />}
        {hasPermission("REASSIGN_CASE") && <ReassignCaseModal caseId={caseId} onDone={onDone} />}
        {canReleaseOwn && <ReleaseCaseModal caseId={caseId} userId={user.user_id} onDone={onDone} />}
      </div>
    </section>
  );
}
