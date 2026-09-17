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
  recipe?: {
    prefab: string; amount: number; station: string;
    ingredients: { prefab: string; name: string; amount: number; sprite?: SpriteDescriptor | null }[];
  };
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

export function visibleSoloLevelingGroups(data: SoloLevelingData) {
  return data.groups.filter((group) => group.id !== "config" && group.id !== "effects");
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
  return data.groups
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
