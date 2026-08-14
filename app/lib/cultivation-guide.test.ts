import { describe, expect, it } from "vitest";

import itemPayload from "@/public/data/items.json";
import { buildCultivationStages } from "./cultivation-guide";
import { parseItemCatalog } from "./item-catalog";

const expectedPillIds = [
  "jq",
  "dt",
  "zj",
  "xs",
  "hj",
  "yz",
  "sm",
  "rl",
  "jy",
  "yx",
  "ns",
  "hs",
  "hy",
  "hl",
  "kx",
].map((suffix) => `tu_tien:xd_danyao_${suffix}`);

describe("cultivation guide data", () => {
  it("resolves the fifteen reviewed stages and their catalog recipes in cultivation order", () => {
    const items = parseItemCatalog(itemPayload);
    const itemsById = new Map(items.map((item) => [item.id, item]));
    const stages = buildCultivationStages(items);

    expect(stages.map((stage) => stage.pill.id)).toEqual(expectedPillIds);
    expect(stages.map((stage) => stage.rank)).toEqual([
      1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    ]);
    expect(stages[0]).toMatchObject({
      currentRealm: "Luyện Khí Sơ Kỳ",
      resultingRealm: "Luyện Khí Trung Kỳ",
    });
    expect(stages[14]).toMatchObject({
      currentRealm: "Hóa Thần Hậu Kỳ",
      resultingRealm: "Phản Hư Sơ Kỳ",
      breakthrough: true,
    });

    for (const stage of stages) {
      expect(stage.recipe.ingredients.length).toBeGreaterThan(0);
      for (const ingredient of stage.recipe.ingredients) {
        expect(itemsById.has(ingredient.id), ingredient.id).toBe(true);
      }
    }

    expect(stages[1].recipe.ingredients.map((ingredient) => ingredient.id)).toEqual([
      "base_game:pigskin",
      "base_game:redgem",
      "tu_tien:xd_lingshi1",
    ]);
  });

  it("fails clearly when a cultivation pill is missing", () => {
    const items = parseItemCatalog(itemPayload).filter(
      (item) => item.id !== "tu_tien:xd_danyao_jq",
    );

    expect(() => buildCultivationStages(items)).toThrow(
      /missing cultivation pill.*tu_tien:xd_danyao_jq/i,
    );
  });

  it("fails clearly when a cultivation pill has no recipe", () => {
    const items = parseItemCatalog(itemPayload).map((item) =>
      item.id === "tu_tien:xd_danyao_jq" ? { ...item, recipe: null } : item,
    );

    expect(() => buildCultivationStages(items)).toThrow(
      /cultivation pill.*tu_tien:xd_danyao_jq.*missing a recipe/i,
    );
  });

  it("fails clearly when a recipe ingredient is absent from the catalog", () => {
    const items = parseItemCatalog(itemPayload).filter(
      (item) => item.id !== "base_game:spidergland",
    );

    expect(() => buildCultivationStages(items)).toThrow(
      /recipe ingredient.*base_game:spidergland.*missing from the catalog/i,
    );
  });
});
