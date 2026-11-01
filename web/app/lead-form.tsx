"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function LeadForm() {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [consent, setConsent] = useState(false);
  const [state, setState] = useState<{ kind: "idle" } | { kind: "busy" } | { kind: "ok"; msg: string } | { kind: "err"; msg: string }>({ kind: "idle" });

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setState({ kind: "busy" });
    try {
      const res = await fetch(`${API}/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, consent }),
      });
      const data = await res.json();
      if (!res.ok) {
        const msg = Array.isArray(data.detail) ? data.detail.map((d: { msg: string }) => d.msg).join("; ") : JSON.stringify(data.detail);
        setState({ kind: "err", msg });
        return;
      }
      setState({ kind: "ok", msg: data.message });
    } catch (err) {
      setState({ kind: "err", msg: String(err) });
    }
  }

  if (state.kind === "ok") {
    return <div style={{ background: "#e8f7ee", padding: 20, borderRadius: 10 }}>{state.msg}</div>;
  }

  return (
    <form onSubmit={submit} style={{ background: "#fff", borderRadius: 10, padding: 20, border: "1px solid #e4e6ea", display: "grid", gap: 12 }}>
      <h2 style={{ margin: 0, fontSize: 18 }}>Get a call from the advisor</h2>
      <label>
        Name
        <input required value={name} onChange={(e) => setName(e.target.value)} style={input} />
      </label>
      <label>
        Mobile number
        <input required type="tel" placeholder="98765 43210" value={phone} onChange={(e) => setPhone(e.target.value)} style={input} />
      </label>
      <p style={{ margin: 0, fontSize: 13, color: "#555" }}>The advisor will ask whether you prefer English, Hindi, Telugu or Tamil.</p>
      <label style={{ display: "flex", gap: 8, alignItems: "flex-start", fontSize: 14 }}>
        <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
        <span>I agree to receive a call from an AI-assisted advisor about motor insurance.</span>
      </label>
      {state.kind === "err" && <div style={{ color: "#b00020", fontSize: 14 }}>{state.msg}</div>}
      <button disabled={state.kind === "busy" || !consent} style={{ padding: "10px 16px", borderRadius: 8, border: 0, background: "#1f4fd8", color: "#fff", fontWeight: 600 }}>
        {state.kind === "busy" ? "Placing call…" : "Call me now"}
      </button>
    </form>
  );
}

const input: React.CSSProperties = { display: "block", width: "100%", marginTop: 4, padding: 8, borderRadius: 6, border: "1px solid #cfd3da", boxSizing: "border-box" };
