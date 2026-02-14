export type Emitter = {
  id: string;
  name: string;
  confidence: number;
  lastSeen: string;
};

export const mockEmitters: Emitter[] = [
  { id: "em-001", name: "Permian Candidate 1", confidence: 0.88, lastSeen: "2026-02-12" },
  { id: "em-002", name: "Turkmenistan Candidate 7", confidence: 0.74, lastSeen: "2026-02-11" }
];
