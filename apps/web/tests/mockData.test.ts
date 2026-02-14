import { describe, expect, it } from "vitest";

import { mockEmitters } from "../lib/mockData";

describe("mockEmitters", () => {
  it("contains seed emitters for dashboard placeholder", () => {
    expect(mockEmitters.length).toBeGreaterThan(0);
    expect(mockEmitters[0]).toHaveProperty("id");
  });
});
