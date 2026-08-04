import { describe, expect, it } from "vitest";

import type { ItemListEntry } from "./item-catalog";
import { buildCultivationStages } from "./cultivation-guide";

const pillIds = [
  "jq", "dt", "zj", "xs", "hj", "yz", "sm", "rl", "jy", "yx", "ns", "hs", "hy", "hl", "kx",
] as const;

function item(id: string, name: string, recipe = true): ItemListEntry {
  return {
    id,
    prefabId: id.split(":")[1],
    namespace: id.startsWith("tu_tien:") ? "tu_tien" : "base_game",
    category: recipe ? "pill" : "item",
    name,
    englishName: null,
    description: null,
    craftingNote: null,
    sprite: null,
    recipe: recipe
      ? {
          outputCount: 1,
          ingredients: [{ id: "base_game:pigskin", name: "Pig Skin", amount: 3, sprite: null }],
        }
      : null,
    wiki: null,
  };
}

describe("cultivation guide data", () => {
  it("maps the fifteen reviewed pill steps in cultivation order", () => {
    const stages = buildCultivationStages([
      ...pillIds.map((pillId) => item(`tu_tien:xd_danyao_${pillId}`, pillId)),
      item("base_game:trunk_summer", "Koalefant Trunk", false),
    ]);

    expect(stages).toHaveLength(15);
    expect(stages.map((stage) => stage.rank)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]);
    expect(stages[0]).toMatchObject({
      currentRealm: "Luyện Khí Sơ Kỳ",
      resultingRealm: "Luyện Khí Trung Kỳ",
    });
    expect(stages[14]).toMatchObject({
      currentRealm: "Hóa Thần Hậu Kỳ",
      resultingRealm: "Phản Hư Sơ Kỳ",
      breakthrough: true,
    });
  });

  it("adds the verified Vòi Voi correction to Đoán Thể Hoàn", () => {
    const stages = buildCultivationStages([
      ...pillIds.map((pillId) => item(`tu_tien:xd_danyao_${pillId}`, pillId)),
      item("base_game:trunk_summer", "Koalefant Trunk", false),
    ]);

    expect(stages[1].recipe?.ingredients[0]).toEqual({
      id: "base_game:trunk_summer",
      name: "Vòi Voi",
      amount: 1,
      sprite: null,
    });
  });
});
