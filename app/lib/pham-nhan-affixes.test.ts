import { describe, expect, it } from "vitest";

import data from "@/data/generated/solo-leveling.json";
import { buildPhamNhanAffixes, filterPhamNhanAffixes } from "@/app/lib/pham-nhan-affixes";

describe("Phàm Nhân affixes", () => {
  it("publishes every extracted affix with the runtime rarity split", () => {
    const affixes = buildPhamNhanAffixes(data);

    expect(affixes).toHaveLength(80);
    expect(affixes.filter((affix) => affix.rarity === "common")).toHaveLength(57);
    expect(affixes.filter((affix) => affix.rarity === "rare")).toHaveLength(14);
    expect(affixes.filter((affix) => affix.rarity === "super-rare")).toHaveLength(9);
  });

  it("searches Vietnamese text and ids, then filters by rarity", () => {
    const affixes = buildPhamNhanAffixes(data);

    expect(filterPhamNhanAffixes(affixes, "mien nhiem lanh", "all").some((affix) => affix.id === "add_immune_cold")).toBe(true);
    expect(filterPhamNhanAffixes(affixes, "special_xwsh", "super-rare").map((affix) => affix.id)).toEqual(["special_xwsh"]);
  });
});
