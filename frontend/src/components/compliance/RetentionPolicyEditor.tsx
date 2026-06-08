"use client";

import { useState } from "react";
import { updateRetentionPolicy } from "@/services/retentionService";
import type { RetentionPolicy } from "@/types/retention.types";

export function RetentionPolicyEditor({ policy, onSaved }: { policy: RetentionPolicy; onSaved: (policy: RetentionPolicy) => void }) {
  const [retentionDays, setRetentionDays] = useState(policy.retention_days);
  const [message, setMessage] = useState("");

  async function save() {
    const saved = await updateRetentionPolicy(policy.data_category, { retention_days: retentionDays, purge_after_days: retentionDays });
    onSaved(saved);
    setMessage("Saved");
  }

  return (
    <div className="inline-form">
      <label>{policy.data_category}</label>
      <input type="number" value={retentionDays} onChange={(event) => setRetentionDays(Number(event.target.value))} />
      <button type="button" onClick={save}>Save</button>
      <span>{message}</span>
    </div>
  );
}
