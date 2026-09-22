import { normalizeSoloSearch } from "@/app/lib/solo-leveling";
import type { SpriteDescriptor } from "@/app/lib/item-catalog";

export type PhamNhanRecipe = { id: string; kind: string; product: string; amount: number; ingredients: { prefab: string; name: string; amount: number; sprite: SpriteDescriptor | null }[]; station: string; conditions: string[] };
export type PhamNhanItem = { id: string; prefab: string; name: string; sprite: SpriteDescriptor | null; category: string; description: string; details: string[]; recipeStatus: "known" | "none" | "unknown"; recipes: PhamNhanRecipe[]; acquisition: { text: string }[]; relatedIds: string[] };
export type PhamNhanSnapshot = { meta: { name: string; version: string }; items: PhamNhanItem[]; affixes: { id: string; name: string; description: string; details: string[]; rarity: string; sprite: SpriteDescriptor | null }[]; guides: { id: string; title: string; text: string }[]; config: { key: string; label: string; description: string; default: string | number | boolean; choices: { label: string; value: string | number | boolean }[] }[] };

export function filterPhamNhanItems(items: PhamNhanItem[], query: string, category: string) {
  const terms = normalizeSoloSearch(query).split(/\s+/).filter(Boolean);
  return items.filter((item) => category === "all" || item.category === category).filter((item) => {
    const haystack = normalizeSoloSearch([item.name, item.prefab, item.description, ...item.details, ...item.recipes.flatMap((recipe) => [recipe.station, ...recipe.ingredients.map((ingredient) => `${ingredient.prefab} ${ingredient.name}`)]), ...item.acquisition.map((entry) => entry.text)].join(" "));
    return terms.every((term) => haystack.includes(term));
  });
}
