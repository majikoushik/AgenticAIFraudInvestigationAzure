"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { NotificationList } from "@/components/notifications/NotificationList";
import { archiveNotification, getMyNotifications, markAllAsRead, markAsRead } from "@/services/notificationService";
import type { NotificationResponse } from "@/types/notification.types";

export default function NotificationsPage() {
  const [items, setItems] = useState<NotificationResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const doRefresh = async () => {
      try {
        const result = await getMyNotifications({ limit: 100 });
        if (mounted) setItems(result.notifications);
      } catch (err) {
        if (mounted) setError((err as Error).message);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    doRefresh();
    return () => { mounted = false; };
  }, []);

  async function read(id: string) {
    await markAsRead(id);
    await refresh();
  }

  async function archive(id: string) {
    await archiveNotification(id);
    await refresh();
  }

  async function refresh() {
    setLoading(true);
    try {
      const result = await getMyNotifications({ limit: 100 });
      setItems(result.notifications);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function readAll() {
    await markAllAsRead();
    await refresh();
  }

  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Notifications" subtitle="In-app workflow notifications and delivery status." />
        <section className="content grid">
          <div className="page-heading"><button className="button secondary" onClick={readAll}>Mark all read</button></div>
          {loading ? <LoadingSpinner label="Loading notifications" /> : error ? <ErrorMessage message={error} /> : <NotificationList notifications={items} onRead={read} onArchive={archive} />}
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
