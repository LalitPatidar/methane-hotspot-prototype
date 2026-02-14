import { EmitterList } from "@/components/EmitterList";

export default function Home() {
  return (
    <main style={{ padding: "1rem" }}>
      <h1>Methane Hotspot Map Dashboard</h1>
      <div
        style={{
          border: "1px solid #ccc",
          background: "#f7f7f7",
          borderRadius: 8,
          minHeight: 280,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: 16
        }}
      >
        <p>Map placeholder (MapLibre/Leaflet will be wired in next PR).</p>
      </div>
      <EmitterList />
    </main>
  );
}
