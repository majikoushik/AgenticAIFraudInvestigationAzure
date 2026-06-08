"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { NotificationTestPanel } from "@/components/notifications/NotificationTestPanel";
import { getAdminNotificationHealth } from "@/services/notificationService";

export default function AdminNotificationsPage() {
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    getAdminNotificationHealth().then(setHealth).catch(() => setHealth({ enabled: false }));
  }, []);

  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Notification Admin" subtitle="Safe notification health and local test dispatch." />
        <section className="content grid">
          <section className="card">
            <div className="card-header"><h3>Health</h3><p>Secret channel values are never returned.</p></div>
            <div className="card-body"><pre className="code-block">{JSON.stringify(health, null, 2)}</pre></div>
          </section>
          <NotificationTestPanel />
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
