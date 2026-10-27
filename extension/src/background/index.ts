// Background service worker: calls the backend, falls back to local rules if it's down.
import type { Action, ActionResult, EmailData, Message } from "../shared/types";
import { getBackendUrl, recordUsage } from "../shared/storage";
import { localClassify, localReply, localSummarize, localTasks } from "../shared/local";

const ENDPOINTS: Record<Action, string> = {
  summarize: "/api/summarize",
  reply: "/api/reply",
  tasks: "/api/tasks",
  classify: "/api/classify",
};

function runLocal(action: Action, email: EmailData, tone?: string): string {
  switch (action) {
    case "summarize": return localSummarize(email);
    case "reply": return localReply(email, tone);
    case "tasks": return localTasks(email);
    case "classify": return localClassify(email);
  }
}

async function runAction(action: Action, email: EmailData, tone?: string): Promise<ActionResult> {
  await recordUsage(action);
  try {
    const base = await getBackendUrl();
    const res = await fetch(base + ENDPOINTS[action], {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...email, tone }),
      signal: AbortSignal.timeout(15000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return {
      ok: true,
      text: data.result,
      source: data.source === "llm" ? "backend" : "local",
      rag: data.rag,
      ragChunks: data.rag_chunks_used,
    };
  } catch {
    return { ok: true, text: runLocal(action, email, tone), source: "local" };
  }
}

chrome.runtime.onMessage.addListener((msg: Message, _sender, sendResponse) => {
  if (msg.type === "RUN_ACTION") {
    runAction(msg.action, msg.email, msg.tone).then(sendResponse);
    return true; // keep the channel open for the async response
  }
  return false;
});
