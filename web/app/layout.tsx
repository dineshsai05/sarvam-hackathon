export const metadata = { title: "AI Motor Insurance Advisor" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui, sans-serif", margin: 0, background: "#f6f7f9" }}>{children}</body>
    </html>
  );
}
