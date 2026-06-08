"use client";

import { useEffect, useState } from "react";
import { getMyPreferences, updateMyPreferences } from "@/services/notificationService";
import type { NotificationChannel, NotificationPreference } from "@/types/notification.types";

const channels: NotificationChannel[] = ["IN_APP", "LOCAL", "EMAIL", "TEAMS", "WEBHOOK"];

export function NotificationPreferencesPanel() {
  const [prefs, setPrefs] = useState<NotificationPreference | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    getMyPreferences().then(setPrefs).catch((err: Error) => setMessage(err.message));
  }, []);

  async function save(next: NotificationPreference) {
    setPrefs(next);
    setPrefs(await updateMyPreferences(next));
    setMessage("Preferences saved.");
  }

  if (!prefs) return <div className="empty-state">{message ?? "Loading preferences."}</div>;

  return (
    <section className="card">
      <div className="card-header">
        <h3>Notification Preferences</h3>
        <p>Choose local MVP channels and quiet-hour metadata.</p>
      </div>
      <div className="card-body form-grid">
        <label className="checkbox-row"><input type="checkbox" checked={prefs.enabled} onChange={(event) => save({ ...prefs, enabled: event.target.checked })} /> Enable notifications</label>
        <div className="panel-list">
          {channels.map((channel) => (
            <label className="checkbox-row" key={channel}>
              <input
                type="checkbox"
                checked={prefs.channels.includes(channel)}
                onChange={(event) => save({ ...prefs, channels: event.target.checked ? [...prefs.channels, channel] : prefs.channels.filter((item) => item !== channel) })}
              />
              {channel}
            </label>
          ))}
        </div>
        {message && <p className="caption">{message}</p>}
      </div>
    </section>
  );
}
