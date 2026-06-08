"use client";

import Link from "next/link";
import { useAuth } from "@/auth/useAuth";

export function Sidebar() {
  const { hasPermission } = useAuth();
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <strong>Agentic AI Fraud Investigation</strong>
        <span>Banking operations console</span>
      </div>
      <nav className="sidebar-nav" aria-label="Primary navigation">
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/cases">Cases</Link>
        {hasPermission("VIEW_OWN_QUEUE") && <Link href="/queues/my">My Queue</Link>}
        {hasPermission("VIEW_UNASSIGNED_QUEUE") && <Link href="/queues/unassigned">Unassigned Queue</Link>}
        {hasPermission("VIEW_TEAM_QUEUE") && <Link href="/queues/team">Team Queue</Link>}
        {hasPermission("VIEW_TEAM_QUEUE") && <Link href="/queues/sla-risk">SLA Risk Queue</Link>}
        {hasPermission("VIEW_TEAM_QUEUE") && <Link href="/assignment/workload">Workload</Link>}
        {hasPermission("VIEW_NOTIFICATIONS") && <Link href="/notifications">Notifications</Link>}
        {hasPermission("VIEW_NOTIFICATIONS") && <Link href="/notifications/preferences">Notification Preferences</Link>}
        {hasPermission("SUBMIT_AI_FEEDBACK") && <Link href="/feedback">AI Feedback</Link>}
        {hasPermission("VIEW_AI_FEEDBACK") && <Link href="/feedback/backlog">Improvement Backlog</Link>}
        {hasPermission("VIEW_AI_FEEDBACK") && <Link href="/feedback/analytics">Feedback Analytics</Link>}
        {hasPermission("VIEW_COMPLIANCE") && <Link href="/compliance">Compliance Summary</Link>}
        {hasPermission("VIEW_COMPLIANCE") && <Link href="/compliance/retention">Retention Policies</Link>}
        {hasPermission("VIEW_COMPLIANCE") && <Link href="/compliance/review-queue">Retention Review Queue</Link>}
        {hasPermission("VIEW_COMPLIANCE") && <Link href="/compliance/legal-holds">Legal Holds</Link>}
        {hasPermission("VIEW_COMPLIANCE") && <Link href="/compliance/exports">Compliance Exports</Link>}
        {hasPermission("ADMIN_CONFIG") && <Link href="/alerts">Alerts</Link>}
        {hasPermission("ADMIN_CONFIG") && <Link href="/incidents">Incidents</Link>}
        <Link href="/metrics">Evaluation Metrics</Link>
        {hasPermission("VIEW_METRICS") && <Link href="/cost">Cost Monitoring</Link>}
        {hasPermission("ADMIN_CONFIG") && <Link href="/observability">Observability</Link>}
        {hasPermission("ADMIN_CONFIG") && <Link href="/admin/config">Admin Config</Link>}
        {hasPermission("ADMIN_CONFIG") && <Link href="/admin/notifications">Notification Admin</Link>}
      </nav>
    </aside>
  );
}
