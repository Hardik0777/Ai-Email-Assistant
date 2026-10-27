import { useState } from "react";
import type { Action, ActionResult, EmailData } from "../../shared/types";
import { classifyOnDevice } from "../../shared/onDeviceClassifier";
import { recordUsage } from "../../shared/storage";

const ICONS: Record<string, string> = {
  Urgent: "🔴", Opportunity: "🟣", Meeting: "🔵", Promotional: "⚪", Normal: "🟢",
};
const CONFIDENT = 0.6; // below this, ask the backend AI instead

const ACTIONS: { id: Action; label: string }[] = [
  { id: "summarize", label: "📝 Summarize" },
  { id: "reply", label: "💬 Smart Reply" },
  { id: "tasks", label: "✅ Tasks" },
  { id: "classify", label: "🏷️ Classify" },
];

async function readEmail(): Promise<EmailData | null> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id || !tab.url?.startsWith("https://mail.google.com")) return null;
  try {
    return await chrome.tabs.sendMessage(tab.id, { type: "READ_EMAIL" });
  } catch {
    return null; // content script not loaded yet (refresh Gmail)
  }
}

export default function ActionsTab() {
  const [loading, setLoading] = useState<Action | null>(null);
  const [result, setResult] = useState<ActionResult | null>(null);
  const [error, setError] = useState("");
  const [tone, setTone] = useState("professional");

  async function run(action: Action) {
    setError(""); setResult(null); setLoading(action);
    const email = await readEmail();
    if (!email) {
      setError("Open an email in Gmail first. If one is open, refresh the Gmail tab.");
      setLoading(null);
      return;
    }
    if (action === "classify") {
      // Try the on-device ONNX model first: instant, offline, private.
      try {
        const p = await classifyOnDevice(email);
        if (p.confidence >= CONFIDENT) {
          await recordUsage("classify");
          setResult({ ok: true, text: `${ICONS[p.label]} ${p.label}`, source: "on-device", confidence: p.confidence });
          setLoading(null);
          return;
        }
      } catch (e) {
        console.warn("On-device classifier unavailable, using backend", e);
      }
    }
    const res: ActionResult = await chrome.runtime.sendMessage({ type: "RUN_ACTION", action, email, tone });
    setResult(res);
    setLoading(null);
  }

  return (
    <div>
      <div className="grid">
        {ACTIONS.map((a) => (
          <button key={a.id} className="action" disabled={!!loading} onClick={() => run(a.id)}>
            {loading === a.id ? "Working…" : a.label}
          </button>
        ))}
      </div>
      <label className="row">
        Reply tone
        <select value={tone} onChange={(e) => setTone(e.target.value)}>
          <option value="professional">Professional</option>
          <option value="friendly">Friendly</option>
          <option value="concise">Concise</option>
        </select>
      </label>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="result">
          <pre>
            {result.text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
              part.startsWith("**") ? <b key={i}>{part.slice(2, -2)}</b> : part
            )}
          </pre>
          <div className="meta">
            <span>
              {result.source === "on-device" && `🧠 On-device model · ${Math.round((result.confidence ?? 0) * 100)}% sure`}
              {result.source === "backend" && "✓ Backend"}
              {result.source === "local" && "⚠ Backend fallback (local)"}
              {result.rag === "used" && ` · RAG used ${result.ragChunks} chunk${result.ragChunks === 1 ? "" : "s"}`}
              {result.rag === "no_match" && " · RAG no resume match"}
            </span>
            <button onClick={() => navigator.clipboard.writeText(result.text)}>Copy</button>
          </div>
        </div>
      )}
    </div>
  );
}
