import snapshot from "@/data/manual/tu_tien_danlo_recipes.json";
import type { ItemListEntry, ItemRecipe } from "./item-catalog";

export function buildDanLoCatalog(allItems: readonly ItemListEntry[]) {
  const alternativeNames: Record<string, string> = { spore_small: "Bào Tử Xanh Lục", spore_tall: "Bào Tử Xanh Lam", spore_medium: "Bào Tử Đỏ", trunk_summer: "Vòi Voi Mùa Hè", trunk_winter: "Vòi Voi Mùa Đông" };
  const ingredientNames: Record<string, string> = { asparagus: "Măng Tây", corn: "Bắp", potato: "Khoai Tây", bird_egg: "Trứng", berries: "Quả Mọng", watermelon: "Dưa Hấu", pepper: "Ớt", shroomcake: "Bánh Nấm", tomato: "Cà Chua" };
  const byId = new Map(allItems.map(item => [item.id, item]));
  const resolve = (prefab: string) => {
    const id = `${prefab.startsWith("xd_") ? "tu_tien" : "base_game"}:${prefab}`;
    const item = byId.get(id);
    if (!item) throw new Error(`Đan Lô: missing catalog item ${id}`);
    return item;
  };
  const items: ItemListEntry[] = [];
  let dynamicRecipe: ItemRecipe | undefined;
  for (const entry of snapshot.recipes) {
    const recipe: ItemRecipe = {
      outputCount: 1,
      ingredients: entry.ingredients.map(ingredient => {
        if (ingredientNames[ingredient.prefab] && !byId.has(`base_game:${ingredient.prefab}`)) {
          return { id: `base_game:${ingredient.prefab}`, name: ingredientNames[ingredient.prefab], sprite: null, amount: ingredient.amount };
        }
        const item = resolve(ingredient.prefab);
        return { id: item.id, name: item.name, sprite: item.sprite, amount: ingredient.amount };
      }),
    };
    if (entry.key === "xd_zhuanshu_weapon") {
      dynamicRecipe = recipe;
      continue;
    }
    const item = resolve(entry.key);
    const notes = [entry.timeSeconds === null ? "Luyện tại Đan Lô." : `Luyện tại Đan Lô trong ${entry.timeSeconds} giây.`];
    if (entry.hasPrefn) notes.push("Có điều kiện xử lý riêng khi luyện; chưa xác nhận đầy đủ điều kiện này.");
    if (entry.alternatives.length) {
      recipe.requiredIngredientChoice = entry.alternatives.flat().map(ingredient => {
        if (alternativeNames[ingredient.prefab]) {
          return { id: `base_game:${ingredient.prefab}`, name: alternativeNames[ingredient.prefab], sprite: byId.get(`base_game:${ingredient.prefab}`)?.sprite ?? null, amount: ingredient.amount };
        }
        const choice = resolve(ingredient.prefab);
        return { id: choice.id, name: choice.name, sprite: choice.sprite, amount: ingredient.amount };
      });
      const alternatives = recipe.requiredIngredientChoice.map(ingredient => `${ingredient.name} ×${ingredient.amount}`).join(" hoặc ");
      notes.push(`Ngoài nguyên liệu chính, bắt buộc thêm một trong các lựa chọn: ${alternatives}.`);
    }
    items.push({ ...item, recipe, craftingNote: notes.join(" "), details: item.details ? { ...item.details, recipeStatus: "known" } : item.details });
  }
  if (!dynamicRecipe) throw new Error("Đan Lô: missing specialized weapon recipe");
  items.sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name, "vi"));
  const overrides = new Map(items.map(item => [item.id, item]));
  return { items, dynamicRecipe, referenceItems: allItems.map(item => overrides.get(item.id) ?? item), version: snapshot.modVersion };
}
