"use client";

import Link from "next/link";
import type { NotificationResponse } from "@/types/notification.types";

export function NotificationDropdown({ notifications, onRead }: { notifications: NotificationResponse[]; onRead: (id: string) => void }) {
  return (
    <div className="notification-dropdown">
      {notifications.length === 0 ? <div className="empty-state">No unread notifications.</div> : notifications.slice(0, 5).map((item) => (
        <button key={item.notification_id} className="notification-row" onClick={() => onRead(item.notification_id)}>
          <strong>{item.title}</strong>
          <span>{item.priority}</span>
        </button>
      ))}
      <Link className="button secondary" href="/notifications">View all</Link>
    </div>
  );
}
