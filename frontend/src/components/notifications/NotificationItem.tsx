import Link from "next/link";
import { NotificationPriorityBadge } from "@/components/notifications/NotificationPriorityBadge";
import type { NotificationResponse } from "@/types/notification.types";
import { formatDateTime } from "@/utils/maskingUtils";

export function NotificationItem({ item, onRead, onArchive }: { item: NotificationResponse; onRead: (id: string) => void; onArchive: (id: string) => void }) {
  return (
    <div className="panel-item">
      <div className="provider-row">
        <div>
          <h4>{item.title}</h4>
          <p>{item.message}</p>
          <p className="caption">{formatDateTime(item.created_at)}</p>
        </div>
        <NotificationPriorityBadge priority={item.priority} />
      </div>
      <div className="action-row">
        {item.case_id && <Link className="button secondary" href={`/cases/${item.case_id}`}>Case</Link>}
        {item.incident_id && <Link className="button secondary" href={`/incidents/${item.incident_id}`}>Incident</Link>}
        {!item.read && <button className="button secondary" onClick={() => onRead(item.notification_id)}>Mark read</button>}
        {!item.archived && <button className="button secondary" onClick={() => onArchive(item.notification_id)}>Archive</button>}
      </div>
    </div>
  );
}
