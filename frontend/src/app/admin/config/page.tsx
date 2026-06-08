"use client";

import { Header } from "@/components/common/Header";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Sidebar } from "@/components/common/Sidebar";
import { AdminConfigPage } from "@/components/admin/AdminConfigPage";
import { useAuth } from "@/auth/useAuth";

export default function AdminConfigRoute() {
  const { hasPermission } = useAuth();
  return (
    <ProtectedRoute>
      <div className="app-layout">
        <Sidebar />
        <main className="main-shell">
          <Header title="Admin Configuration" subtitle="Safe non-secret runtime settings, feature flags, validation, health, and history." />
          <section className="content">
            {hasPermission("ADMIN_CONFIG") ? <AdminConfigPage /> : <div className="message error">Permission denied. ADMIN_CONFIG is required.</div>}
          </section>
        </main>
      </div>
    </ProtectedRoute>
  );
}
