"use client";

import { useState } from "react";
import { sendTestNotification } from "@/services/notificationService";

export function NotificationTestPanel() {
  const [message, setMessage] = useState<string | null>(null);

  async function send() {
    const result = await sendTestNotification({
      event_type: "CASE_ASSIGNED",
      recipient_type: "USER",
      recipient_id: "fraud_analyst_01",
      priority: "INFO",
      title: "Test notification",
      message: "This is a local test notification."
    });
    setMessage(`Created ${result.notification_id}`);
  }

  return (
    <section className="card">
      <div className="card-header">
        <h3>Test Notification</h3>
        <p>Creates a local in-app notification without external channels.</p>
      </div>
      <div className="card-body">
        <button className="button" onClick={send}>Send test</button>
        {message && <p className="caption">{message}</p>}
      </div>
    </section>
  );
}
