import type { SpriteDescriptor } from "@/app/lib/item-catalog";

export interface SoloLevelingShopProduct {
  rank?: string;
  currency?: string;
  prefab: string;
  price: number;
  stock: number;
  amount: number;
  sprite: SpriteDescriptor | null;
}

export interface SoloLevelingRecipe {
  prefab: string;
  amount: number;
  station: string;
  ingredients: { prefab: string; name: string; amount: number; sprite?: SpriteDescriptor | null }[];
}

export interface SoloLevelingEntry {
  id: string;
  title: string;
  lines: string[];
  tables: { headers: string[]; rows: string[][] }[];
  source: string;
  shop?: SoloLevelingShopProduct;
  sprite?: SpriteDescriptor | null;
  category?: string;
  rank?: string;
  related?: { prefab: string; name: string; sprite: SpriteDescriptor }[];
  recipe?: SoloLevelingRecipe;
  recipes?: SoloLevelingRecipe[];
  talents?: { id: string; level: number; name: string; desc: string }[];
}

export interface SoloLevelingData {
  meta: { name: string; version: string; author: string; files: number };
  groups: { id: string; title: string; description: string; entries: SoloLevelingEntry[] }[];
  files: { path: string; size: number; sha256: string; text: boolean }[];
}

export function normalizeSoloSearch(value: string): string {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d").replace(/Đ/g, "D").toLowerCase().trim();
}

function prefabFromLines(lines: string[]) {
  return lines
    .find((line) => /^\s*-?\s*Prefab\s*:/i.test(line))
    ?.replace(/^\s*-?\s*Prefab\s*:\s*/i, "")
    .trim()
    .toLowerCase();
}

export function visibleSoloLevelingGroups(data: SoloLevelingData) {
  const wiki = data.groups.find((group) => group.id === "wiki");
  const items = data.groups.find((group) => group.id === "items");
  const crafting = data.groups.find((group) => group.id === "crafting");
  const wikiItems = wiki?.entries
    .map((entry) => ({ entry, prefab: prefabFromLines(entry.lines) }))
    .filter((item): item is { entry: SoloLevelingEntry; prefab: string } => Boolean(item.prefab)) ?? [];
  const wikiByPrefab = new Map(wikiItems.map((item) => [item.prefab, item.entry]));

  if (!items || !crafting) {
    return data.groups.filter((group) => !["wiki", "items", "config", "effects"].includes(group.id));
  }

  const existingPrefabs = new Set(items.entries.map((entry) => prefabFromLines(entry.lines)).filter(Boolean));
  const enrichedEntries = items.entries.map((entry) => {
    const wikiEntry = wikiByPrefab.get(prefabFromLines(entry.lines) ?? "");
    if (!wikiEntry) return entry;
    return {
      ...entry,
      lines: wikiEntry.lines,
      source: wikiEntry.source,
    };
  });
  const movedEntries = wikiItems
    .filter(({ prefab }) => !existingPrefabs.has(prefab))
    .map(({ entry }) => entry);
  const itemEntries = [...enrichedEntries, ...movedEntries];
  const recipesByPrefab = new Map<string, SoloLevelingRecipe[]>();

  for (const entry of crafting.entries) {
    if (!entry.recipe) continue;
    const prefab = entry.recipe.prefab.toLowerCase();
    recipesByPrefab.set(prefab, [...(recipesByPrefab.get(prefab) ?? []), entry.recipe]);
  }

  const mergedEntries = itemEntries.map((entry) => {
    const recipes = recipesByPrefab.get(prefabFromLines(entry.lines) ?? "") ?? [];
    return {
      ...entry,
      category: "Item",
      recipe: recipes[0],
      recipes,
    };
  });
  const mergedPrefabs = new Set(mergedEntries.map((entry) => prefabFromLines(entry.lines)).filter(Boolean));

  for (const [prefab, recipes] of recipesByPrefab) {
    if (mergedPrefabs.has(prefab)) continue;
    const sourceEntry = crafting.entries.find((entry) => entry.recipe?.prefab.toLowerCase() === prefab);
    if (!sourceEntry) continue;
    mergedEntries.push({ ...sourceEntry, category: "Item", recipe: recipes[0], recipes });
  }
  mergedEntries.sort((left, right) => Number(right.recipes.length > 0) - Number(left.recipes.length > 0));

  return data.groups
    .filter((group) => !["wiki", "items", "config", "effects"].includes(group.id))
    .map((group) => {
      if (group.id !== "crafting") return group;
      return {
        ...group,
        title: "Item",
        description: "Vật phẩm, công trình, sinh vật và công thức chế tạo trong Solo Leveling.",
        entries: mergedEntries,
      };
    });
}

// UI browsing groups, not a difficulty field declared by the guild mod.
export function guildQuestDifficulty(rank?: string) {
  if (rank === "E" || rank === "D") return "Dễ";
  if (rank === "C" || rank === "B") return "Vừa";
  if (rank === "A" || rank === "S") return "Khó";
  return undefined;
}

export function filterSoloLeveling(data: SoloLevelingData, query: string, topic: string) {
  const terms = normalizeSoloSearch(query).split(/\s+/).filter(Boolean);
  return visibleSoloLevelingGroups(data)
    .filter((group) => topic === "all" || topic === group.id)
    .map((group) => ({
      ...group,
      entries: group.entries.filter((entry) => {
        const content = normalizeSoloSearch([group.title, entry.title, entry.id, ...entry.lines, ...entry.tables.flatMap((table) => [...table.headers, ...table.rows.flat()])].join(" "));
        return terms.every((term) => content.includes(term));
      }),
    }))
    .filter((group) => group.entries.length > 0);
}
