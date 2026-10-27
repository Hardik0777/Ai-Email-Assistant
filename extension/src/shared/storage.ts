import type { Action, Usage } from "./types";

export const DEFAULT_BACKEND = "http://127.0.0.1:8001";
const MINUTES_SAVED: Record<Action, number> = { summarize: 2, reply: 3, tasks: 2, classify: 0.5 };

const today = () => new Date().toISOString().slice(0, 10);
const emptyUsage = (): Usage => ({ date: today(), processed: 0, counts: { summarize: 0, reply: 0, tasks: 0, classify: 0 } });

export async function getBackendUrl(): Promise<string> {
  const { backendUrl } = await chrome.storage.local.get("backendUrl");
  return backendUrl || DEFAULT_BACKEND;
}

export async function setBackendUrl(url: string) {
  await chrome.storage.local.set({ backendUrl: url.replace(/\/$/, "") });
}

export async function getUsage(): Promise<Usage> {
  const { usage } = await chrome.storage.local.get("usage");
  return usage && usage.date === today() ? usage : emptyUsage();
}

export async function recordUsage(action: Action) {
  const usage = await getUsage();
  usage.processed += 1;
  usage.counts[action] += 1;
  await chrome.storage.local.set({ usage });
}

export async function resetUsage() {
  await chrome.storage.local.set({ usage: emptyUsage() });
}

export function minutesSaved(usage: Usage): number {
  return (Object.keys(usage.counts) as Action[]).reduce((sum, a) => sum + usage.counts[a] * MINUTES_SAVED[a], 0);
}
