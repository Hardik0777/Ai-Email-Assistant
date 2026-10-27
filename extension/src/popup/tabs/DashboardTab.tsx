import { useEffect, useState } from "react";
import type { Action, Usage } from "../../shared/types";
import { getBackendUrl, getUsage, minutesSaved, resetUsage } from "../../shared/storage";

export default function DashboardTab() {
  const [usage, setUsage] = useState<Usage | null>(null);
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking");

  async function refresh() {
    setUsage(await getUsage());
    setStatus("checking");
    try {
      const res = await fetch((await getBackendUrl()) + "/health", { signal: AbortSignal.timeout(3000) });
      setStatus(res.ok ? "online" : "offline");
    } catch {
      setStatus("offline");
    }
  }

  useEffect(() => { refresh(); }, []);
  if (!usage) return null;

  const top = (Object.entries(usage.counts) as [Action, number][]).sort((a, b) => b[1] - a[1])[0];

  return (
    <div>
      <div className="stats">
        <div className="stat"><b>{usage.processed}</b><span>Emails processed today</span></div>
        <div className="stat"><b>{minutesSaved(usage)} min</b><span>Estimated time saved</span></div>
        <div className="stat"><b>{top[1] ? top[0] : "—"}</b><span>Most used feature</span></div>
        <div className="stat"><b className={status}>{status}</b><span>Backend status</span></div>
      </div>
      <div className="row">
        <button onClick={refresh}>Refresh</button>
        <button onClick={async () => { await resetUsage(); refresh(); }}>Reset local usage</button>
      </div>
      <p className="hint">Resume upload for RAG replies arrives in Phase 4.</p>
    </div>
  );
}
