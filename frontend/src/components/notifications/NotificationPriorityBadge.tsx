import type { NotificationPriority } from "@/types/notification.types";

export function NotificationPriorityBadge({ priority }: { priority: NotificationPriority | string }) {
  return <span className={`badge priority-${String(priority).toLowerCase()}`}>{priority}</span>;
}
