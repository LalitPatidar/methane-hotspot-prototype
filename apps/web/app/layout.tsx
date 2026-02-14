import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Methane Hotspot Prototype",
  description: "MVP map and emitter dashboard"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "Arial, sans-serif" }}>{children}</body>
    </html>
  );
}
