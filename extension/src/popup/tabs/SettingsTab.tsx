import { useEffect, useState } from "react";
import { DEFAULT_BACKEND, getBackendUrl, setBackendUrl } from "../../shared/storage";

export default function SettingsTab() {
  const [url, setUrl] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => { getBackendUrl().then(setUrl); }, []);

  async function save() {
    await setBackendUrl(url || DEFAULT_BACKEND);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  }

  return (
    <div>
      <label className="col">
        Backend URL
        <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder={DEFAULT_BACKEND} />
      </label>
      <div className="row">
        <button onClick={save}>{saved ? "Saved ✓" : "Save"}</button>
        <button onClick={() => setUrl(DEFAULT_BACKEND)}>Reset to default</button>
      </div>
    </div>
  );
}
