import { useEffect, useRef, useState } from "react";
import { getBackendUrl } from "../../shared/storage";

interface ResumeInfo {
  filename: string;
  chunks: number;
  sections: string[];
  uploaded_at: string;
}

interface Status {
  has_resume: boolean;
  current: ResumeInfo | null;
}

export default function ResumePanel() {
  const [status, setStatus] = useState<Status | null>(null);
  const [history, setHistory] = useState<ResumeInfo[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);

  async function api(path: string, init?: RequestInit) {
    const res = await fetch((await getBackendUrl()) + path, init);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    return data;
  }

  async function load() {
    try {
      setStatus(await api("/api/resume/status"));
      setHistory(await api("/api/resume/history"));
    } catch {
      setStatus(null);
      setMessage("Start the backend to manage your resume.");
    }
  }

  useEffect(() => { load(); }, []);

  async function upload(file: File) {
    setBusy(true); setMessage("");
    const form = new FormData();
    form.append("file", file);
    try {
      const info: ResumeInfo = await api("/api/resume/upload", { method: "POST", body: form });
      setMessage(`✓ Indexed ${info.chunks} chunks from ${info.sections.length} sections`);
      await load();
    } catch (e) {
      setMessage(`Upload failed: ${(e as Error).message}`);
    } finally {
      setBusy(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  async function remove() {
    setBusy(true);
    try {
      await api("/api/resume", { method: "DELETE" });
      setMessage("Resume deleted");
      await load();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="resume">
      <h4>Resume for Smart Reply</h4>
      {status?.current ? (
        <p className="hint">
          📄 <b>{status.current.filename}</b> · {status.current.chunks} chunks
          <br />Sections: {status.current.sections.join(", ")}
        </p>
      ) : (
        status && <p className="hint">No resume uploaded. Replies won't use resume details.</p>
      )}
      <input
        ref={fileInput}
        type="file"
        accept=".pdf,.docx"
        hidden
        onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])}
      />
      <div className="row">
        <button disabled={busy || !status} onClick={() => fileInput.current?.click()}>
          {busy ? "Working…" : status?.has_resume ? "Replace resume" : "Upload PDF / DOCX"}
        </button>
        {status?.has_resume && <button disabled={busy} onClick={remove}>Delete</button>}
      </div>
      {message && <p className="hint">{message}</p>}
      {history.length > 1 && (
        <details>
          <summary className="hint">Upload history ({history.length})</summary>
          {history.slice().reverse().map((h) => (
            <p key={h.uploaded_at} className="hint">{h.filename} · {new Date(h.uploaded_at).toLocaleString()}</p>
          ))}
        </details>
      )}
    </div>
  );
}
