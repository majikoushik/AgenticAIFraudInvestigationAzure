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
        {hasPermission("ADMIN_CONFIG") && <Link href="/alerts">Alerts</Link>}
        {hasPermission("ADMIN_CONFIG") && <Link href="/incidents">Incidents</Link>}
        <Link href="/metrics">Evaluation Metrics</Link>
        {hasPermission("VIEW_METRICS") && <Link href="/cost">Cost Monitoring</Link>}
        {hasPermission("ADMIN_CONFIG") && <Link href="/observability">Observability</Link>}
        {hasPermission("ADMIN_CONFIG") && <Link href="/dashboard">Admin Config</Link>}
      </nav>
    </aside>
  );
}
