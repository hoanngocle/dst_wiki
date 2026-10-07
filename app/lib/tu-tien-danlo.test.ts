import { expect, it } from "vitest";
import itemsPayload from "@/public/data/items.json";
import { parseItemPayload } from "./item-catalog";
import { buildDanLoCatalog } from "./tu-tien-danlo";

it("resolves all 78 furnace recipes without inventing a prefab for the dynamic weapon", () => {
  const result = buildDanLoCatalog(parseItemPayload(itemsPayload));
  expect(result.items).toHaveLength(77);
  expect(new Set(result.items.map(i => i.id)).size).toBe(77);
  expect(result.items.some(i => i.prefabId === "xd_zhuanshu_weapon")).toBe(false);
  expect(result.dynamicRecipe.ingredients).toHaveLength(4);
  const tnz = result.items.find(i => i.prefabId === "xd_wmz_tnz")!;
  expect(Object.fromEntries(tnz.recipe!.ingredients.map(i => [i.id, i.amount]))).toEqual({
    "tu_tien:xd_zcmy": 2, "base_game:greengem": 10,
    "base_game:goldnugget": 5, "tu_tien:xd_lingshi3": 3,
  });
  expect(result.items.find(i => i.prefabId === "xd_dy_tsfhd")!.craftingNote).toContain("120 giây");
  expect(result.items.find(i => i.prefabId === "xd_yhbs")!.craftingNote).toContain("điều kiện");
});

it("includes required choice ingredients in addition to the main pill ingredients", () => {
  const { items } = buildDanLoCatalog(parseItemPayload(itemsPayload));
  const choices = (key: string) => items.find(item => item.prefabId === key)!.recipe!.requiredIngredientChoice;
  expect(choices("xd_danyao_dt")?.map(i => [i.id, i.amount])).toEqual([
    ["base_game:trunk_summer", 1], ["base_game:trunk_winter", 1],
  ]);
  expect(choices("xd_danyao_bg")?.map(i => [i.id, i.amount])).toEqual([
    ["base_game:trunk_summer", 1], ["base_game:trunk_winter", 1],
  ]);
  expect(choices("xd_danyao_yz")?.map(i => [i.id, i.amount])).toEqual([
    ["base_game:spore_small", 10], ["base_game:spore_tall", 10], ["base_game:spore_medium", 10],
  ]);
});


it("keeps source-backed rare materials available in furnace recipes and ingredient dialogs", () => {
  const result = buildDanLoCatalog(parseItemPayload(itemsPayload));
  for (const prefab of ["horrorfuel", "purebrilliance", "livinglog"]) {
    const id = `base_game:${prefab}`;
    const reference = result.referenceItems.find(item => item.id === id);
    expect(reference).toBeDefined();
    expect(reference!.prefabId).toBe(prefab);
    expect(reference!.sprite).not.toBeNull();
    expect(result.items.some(item => item.recipe!.ingredients.some(ingredient => ingredient.id === id))).toBe(true);
  }
});
