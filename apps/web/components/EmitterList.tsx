import { mockEmitters } from "@/lib/mockData";

export function EmitterList() {
  return (
    <section>
      <h2>Persistent Emitters (placeholder)</h2>
      <ul>
        {mockEmitters.map((emitter) => (
          <li key={emitter.id}>
            <strong>{emitter.name}</strong> — confidence: {emitter.confidence} — last seen: {emitter.lastSeen}
          </li>
        ))}
      </ul>
    </section>
  );
}
