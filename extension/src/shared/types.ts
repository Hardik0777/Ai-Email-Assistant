export interface EmailData {
  threadId: string;
  subject: string;
  sender: string;
  body: string;
}

export type Action = "summarize" | "reply" | "tasks" | "classify";

export type Message =
  | { type: "READ_EMAIL" }
  | { type: "RUN_ACTION"; action: Action; email: EmailData; tone?: string };

export interface ActionResult {
  ok: boolean;
  text: string;
  source: "backend" | "local" | "on-device";
  confidence?: number;
  rag?: "used" | "no_match" | "no_resume";
  ragChunks?: number;
}

export interface Usage {
  date: string;
  processed: number;
  counts: Record<Action, number>;
}
