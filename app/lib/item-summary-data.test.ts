import { describe, expect, it } from "vitest";
import payload from "@/public/data/items.json";
import { parseItemPayload, type ItemSummaryData } from "./item-catalog";

describe("published item summaries", () => {
  it("gives every retained base item usage and acquisition without repeated generated prose", () => {
    for (const item of payload.items.filter((entry) => entry.namespace === "base_game" && entry.category === "item")) {
      for (const field of ["usage", "acquisition"] as const) {
        const fact = item.summary[field];
        expect(fact.status, `${item.id}/${field}`).toBe("known");
        expect(fact.text, `${item.id}/${field}`).not.toMatch(/Shipwrecked|Hamlet|Reign of Giants|xd_/i);
      }
      expect((item.summary.usage.text?.match(/Dùng làm nguyên liệu chế tạo/g) ?? []).length, item.id).toBeLessThanOrEqual(1);
    }
  });

  it("preserves DST mechanics and excludes duplicate and character-dependent records", () => {
    const byId = new Map(payload.items.map((item) => [item.id, item]));
    expect(byId.get("base_game:messagebottle")?.summary.usage.text).toContain("Sunken Chest");
    expect(byId.get("base_game:shadowheart")?.summary.acquisition.text).toContain("cấp 3");
    expect(byId.get("wiki:95716")?.summary.usage.text).toContain("1 Bone Shards");
    expect(byId.get("base_game:slurper_pelt")?.summary.usage.text).not.toContain("Khi ăn");
    for (const id of ["base_game:slurperpelt", "base_game:lucy", "base_game:scandata", "wiki:49191"]) {
      expect(byId.has(id), id).toBe(false);
    }
  });

  it("provides four validated facts for every published entry", () => {
    for (const item of payload.items) {
      expect(Object.keys(item.summary).sort()).toEqual(["acquisition", "fuel", "recycling", "usage"]);
      for (const fact of Object.values(item.summary as ItemSummaryData)) {
        if (fact.status === "known") {
          expect(fact.text?.trim().length).toBeGreaterThan(0);
          expect(fact.sources.length).toBeGreaterThan(0);
        } else {
          expect(["unknown", "not_applicable"]).toContain(fact.status);
          expect(fact.text).toBeNull();
        }
      }
    }
    expect(parseItemPayload(payload).every((item) => item.summary)).toBe(true);
  });

  it("keeps Advert's four facts separate and rejects an incomplete summary", () => {
    const advert = payload.items.find((item) => item.id === "base_game:tacklesketch")!;
    expect(advert.summary.fuel.text).toContain("15 giây");
    expect(advert.summary.recycling.text).toContain("Bàn vẽ bản đồ");
    expect(advert.summary.acquisition.text).toContain("cấp 6");
    expect(advert.craftingNote).toBeNull();
    expect(() => parseItemPayload({ schema_version: 7, items: [{ ...advert, summary: { usage: advert.summary.usage } }] })).toThrow(/summary.fuel/);
  });
});
