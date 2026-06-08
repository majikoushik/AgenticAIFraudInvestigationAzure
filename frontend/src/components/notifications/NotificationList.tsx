"use client";

import { NotificationItem } from "@/components/notifications/NotificationItem";
import type { NotificationResponse } from "@/types/notification.types";

export function NotificationList({ notifications, onRead, onArchive }: { notifications: NotificationResponse[]; onRead: (id: string) => void; onArchive: (id: string) => void }) {
  return (
    <section className="card">
      <div className="card-header">
        <h3>Notifications</h3>
        <p>{notifications.length} notifications in this view.</p>
      </div>
      <div className="card-body panel-list">
        {notifications.length === 0 ? <div className="empty-state">No notifications found.</div> : notifications.map((item) => <NotificationItem key={item.notification_id} item={item} onRead={onRead} onArchive={onArchive} />)}
      </div>
    </section>
  );
}
