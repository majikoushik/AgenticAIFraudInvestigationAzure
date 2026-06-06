import Link from "next/link";

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <strong>Agentic AI Fraud Investigation</strong>
        <span>Banking operations console</span>
      </div>
      <nav className="sidebar-nav" aria-label="Primary navigation">
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/cases">Cases</Link>
      </nav>
    </aside>
  );
}
