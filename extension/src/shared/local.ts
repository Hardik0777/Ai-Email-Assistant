// Offline fallbacks used when the backend isn't running. Simple rules, no AI.
import type { EmailData } from "./types";

const sentences = (text: string) =>
  text.replace(/\s+/g, " ").split(/(?<=[.!?])\s+/).filter((s) => s.length > 20);

export function localSummarize(email: EmailData): string {
  const top = sentences(email.body).slice(0, 3);
  return top.length ? top.map((s) => `• ${s}`).join("\n") : "Email is too short to summarize.";
}

export function localReply(email: EmailData, tone = "professional"): string {
  const name = email.sender.split(/[<@]/)[0].trim() || "there";
  const opener = tone === "friendly" ? `Hi ${name}!` : `Hello ${name},`;
  return `${opener}\n\nThank you for your email regarding "${email.subject}". I'll review it and get back to you shortly.\n\nBest regards`;
}

export function localTasks(email: EmailData): string {
  const pattern = /\b(please|kindly|need to|must|should|deadline|by (monday|tuesday|wednesday|thursday|friday|tomorrow|today|eod)|due)\b/i;
  const tasks = sentences(email.body).filter((s) => pattern.test(s));
  return tasks.length ? tasks.map((t) => `☐ ${t}`).join("\n") : "No tasks or deadlines found.";
}

export function localClassify(email: EmailData): string {
  const text = `${email.subject} ${email.body}`.toLowerCase();
  if (/(urgent|asap|immediately|deadline|today)/.test(text)) return "🔴 Urgent";
  if (/(interview|offer|opportunity|hiring|position)/.test(text)) return "🟣 Opportunity";
  if (/(unsubscribe|newsletter|sale|discount)/.test(text)) return "⚪ Promotional";
  if (/(meeting|schedule|call|invite)/.test(text)) return "🔵 Meeting";
  return "🟢 Normal";
}
