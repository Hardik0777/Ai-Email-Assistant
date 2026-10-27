// Runs inside Gmail. Reads the currently open email when the popup asks for it.
import type { EmailData, Message } from "../shared/types";

function readOpenEmail(): EmailData | null {
  const subject = document.querySelector("h2.hP")?.textContent?.trim();
  if (!subject) return null; // no email is open

  // A thread can contain several messages; read the last expanded one.
  const bodies = document.querySelectorAll<HTMLElement>("div.a3s.aiL, div.a3s");
  const senders = document.querySelectorAll<HTMLElement>("span.gD");
  const body = bodies[bodies.length - 1]?.innerText?.trim() ?? "";
  const lastSender = senders[senders.length - 1];
  const sender = lastSender?.getAttribute("name") || lastSender?.textContent?.trim() || "Unknown";
  const threadId = location.hash.split("/").pop() || "unknown";

  return { threadId, subject, sender, body };
}

chrome.runtime.onMessage.addListener((msg: Message, _sender, sendResponse) => {
  if (msg.type === "READ_EMAIL") sendResponse(readOpenEmail());
  return false;
});
