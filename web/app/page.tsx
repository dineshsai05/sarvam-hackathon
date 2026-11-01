import LeadForm from "./lead-form";

const PLANS = [
  { name: "Third-party", blurb: "Mandatory cover for damage you cause to others. Lowest premium." },
  { name: "Own-damage", blurb: "Covers your own car for accident, theft, fire and natural calamities." },
  { name: "Comprehensive", blurb: "Third-party + own-damage, with optional add-ons like zero depreciation." },
];

export default function Home() {
  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "48px 20px" }}>
      <h1 style={{ marginBottom: 8 }}>Private car insurance, explained by voice</h1>
      <p style={{ color: "#555", marginTop: 0 }}>
        Leave your number and our AI advisor will call you in your language to compare policies for your car.
      </p>

      <section style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", margin: "28px 0" }}>
        {PLANS.map((p) => (
          <div key={p.name} style={{ background: "#fff", borderRadius: 10, padding: 16, border: "1px solid #e4e6ea" }}>
            <strong>{p.name}</strong>
            <p style={{ color: "#555", fontSize: 14, margin: "6px 0 0" }}>{p.blurb}</p>
          </div>
        ))}
      </section>

      <LeadForm />

      <p style={{ fontSize: 12, color: "#777", marginTop: 32 }}>
        This is an educational comparison and lead-assistance tool. You will be speaking with an AI agent. We are not
        an IRDAI-licensed intermediary; quotes shown are samples unless stated otherwise.
      </p>
    </main>
  );
}
