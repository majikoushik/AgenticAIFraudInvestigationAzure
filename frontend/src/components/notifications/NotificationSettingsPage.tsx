"use client";

import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { NotificationPreferencesPanel } from "@/components/notifications/NotificationPreferencesPanel";

export function NotificationSettingsPage() {
  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Notification Preferences" subtitle="Manage local notification channels and event preferences." />
        <section className="content">
          <NotificationPreferencesPanel />
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
