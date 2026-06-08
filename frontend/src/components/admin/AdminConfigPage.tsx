"use client";

import { useEffect, useMemo, useState } from "react";
import { ConfigCategoryTabs } from "@/components/admin/ConfigCategoryTabs";
import { ConfigHealthPanel } from "@/components/admin/ConfigHealthPanel";
import { ConfigHistoryPanel } from "@/components/admin/ConfigHistoryPanel";
import { ConfigItemEditor } from "@/components/admin/ConfigItemEditor";
import { ConfigResetPanel } from "@/components/admin/ConfigResetPanel";
import { ConfigValidationErrors } from "@/components/admin/ConfigValidationErrors";
import { FeatureFlagPanel } from "@/components/admin/FeatureFlagPanel";
import { SecretRedactionNotice } from "@/components/admin/SecretRedactionNotice";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { getAdminConfigDashboard, resetAdminConfig, updateAdminConfig, updateFeatureFlag } from "@/services/adminConfigService";
import type { AdminConfigCategory, AdminConfigHistoryRecord, ConfigHealthResponse, FeatureFlag } from "@/types/adminConfig.types";

export function AdminConfigPage() {
  const [categories, setCategories] = useState<AdminConfigCategory[]>([]);
  const [health, setHealth] = useState<ConfigHealthResponse | null>(null);
  const [history, setHistory] = useState<AdminConfigHistoryRecord[]>([]);
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [active, setActive] = useState("AI_PROVIDER");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Array<{ key: string; errors: string[] }>>([]);

  async function refresh() {
    const dashboard = await getAdminConfigDashboard();
    setCategories(dashboard.config.categories);
    setHealth(dashboard.health);
    setHistory(dashboard.history);
    setFlags(dashboard.featureFlags);
  }

  useEffect(() => {
    refresh().catch((err: Error) => setError(err.message)).finally(() => setLoading(false));
  }, []);

  const activeCategory = useMemo(() => categories.find((category) => category.category === active) ?? categories[0], [categories, active]);

  async function saveItem(key: string, value: unknown) {
    const response = await updateAdminConfig({ updates: [{ key, value }], comment: "Updated from admin configuration panel." });
    setValidationErrors(response.validation_errors);
    setMessage(response.message);
    await refresh();
  }

  async function toggleFlag(flag: FeatureFlag, enabled: boolean) {
    await updateFeatureFlag(flag.key, enabled, "Updated from admin configuration panel.");
    setMessage(`${flag.key} updated.`);
    await refresh();
  }

  async function reset() {
    const response = await resetAdminConfig("Reset from admin configuration panel.");
    setMessage(response.message);
    await refresh();
  }

  if (loading) return <LoadingSpinner label="Loading admin configuration" />;
  if (error) return <ErrorMessage message={error} />;
  return (
    <div className="grid metrics-grid">
      <SecretRedactionNotice />
      {message && <div className="message success">{message}</div>}
      <ConfigValidationErrors errors={validationErrors} />
      {health && <ConfigHealthPanel health={health} />}
      <FeatureFlagPanel flags={flags} onToggle={toggleFlag} />
      <section className="panel span-2">
        <h2>Configuration</h2>
        <ConfigCategoryTabs categories={categories} active={activeCategory?.category ?? active} onChange={setActive} />
        <div className="panel-list">
          {(activeCategory?.items ?? []).map((item) => <ConfigItemEditor key={item.key} item={item} onSave={saveItem} />)}
        </div>
      </section>
      <ConfigResetPanel onReset={reset} />
      <ConfigHistoryPanel history={history} />
    </div>
  );
}
