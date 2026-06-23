"use client";

import { useEffect, useState } from "react";
import { NotificationDropdown } from "@/components/notifications/NotificationDropdown";
import { getMyNotifications, getNotificationSummary, markAsRead } from "@/services/notificationService";
import type { NotificationResponse, NotificationSummary } from "@/types/notification.types";

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [summary, setSummary] = useState<NotificationSummary | null>(null);
  const [items, setItems] = useState<NotificationResponse[]>([]);

  useEffect(() => {
    let mounted = true;
    const doRefresh = async () => {
      try {
        const [nextSummary, nextItems] = await Promise.all([getNotificationSummary(), getMyNotifications({ unread_only: true, limit: 5 })]);
        if (mounted) {
          setSummary(nextSummary);
          setItems(nextItems.notifications);
        }
      } catch {
        // ignore
      }
    };
    doRefresh();
    return () => { mounted = false; };
  }, []);

  async function refresh() {
    try {
      const [nextSummary, nextItems] = await Promise.all([getNotificationSummary(), getMyNotifications({ unread_only: true, limit: 5 })]);
      setSummary(nextSummary);
      setItems(nextItems.notifications);
    } catch {
      // ignore
    }
  }

  async function handleRead(id: string) {
    await markAsRead(id);
    await refresh();
  }

  return (
    <div className="notification-bell">
      <button className={`button secondary ${summary?.critical_unread_count ? "notification-critical" : ""}`} onClick={() => setOpen(!open)}>
        Notifications {summary?.unread_count ? `(${summary.unread_count})` : ""}
      </button>
      {open && <NotificationDropdown notifications={items} onRead={handleRead} />}
    </div>
  );
}
