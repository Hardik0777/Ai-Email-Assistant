import { useState } from "react";
import ActionsTab from "./tabs/ActionsTab";
import DashboardTab from "./tabs/DashboardTab";
import SettingsTab from "./tabs/SettingsTab";

const TABS = ["Actions", "Dashboard", "Settings"] as const;
type Tab = (typeof TABS)[number];

export default function App() {
  const [tab, setTab] = useState<Tab>("Actions");
  return (
    <div className="app">
      <header>✉️ AI Email Assistant</header>
      <nav>
        {TABS.map((t) => (
          <button key={t} className={t === tab ? "active" : ""} onClick={() => setTab(t)}>{t}</button>
        ))}
      </nav>
      <main>
        {tab === "Actions" && <ActionsTab />}
        {tab === "Dashboard" && <DashboardTab />}
        {tab === "Settings" && <SettingsTab />}
      </main>
    </div>
  );
}
