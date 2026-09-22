import { normalizeSoloSearch, type SoloLevelingData } from "@/app/lib/solo-leveling";

export type AffixRarity = "common" | "rare" | "super-rare";
export type AffixFilter = "all" | AffixRarity;

export interface PhamNhanAffix {
  id: string;
  name: string;
  description: string;
  details: string[];
  rarity: AffixRarity;
  source: string;
}

function affixRarity(lines: string[]): AffixRarity {
  if (lines.includes("Có thể ép: Có")) return "common";
  if (lines.includes("Chỉ từ ngẫu luyện / siêu boss: Có")) return "super-rare";
  return "rare";
}

export function buildPhamNhanAffixes(data: SoloLevelingData): PhamNhanAffix[] {
  const entries = data.groups.find((group) => group.id === "effects")?.entries ?? [];

  return entries
    .filter((entry) => entry.id.startsWith("enchant-"))
    .map((entry) => ({
      id: entry.id.replace(/^enchant-/, ""),
      name: entry.title,
      description: entry.lines[0] ?? "Chưa có mô tả.",
      details: entry.lines.slice(1),
      rarity: affixRarity(entry.lines),
      source: entry.source,
    }));
}

export function filterPhamNhanAffixes(affixes: PhamNhanAffix[], query: string, rarity: AffixFilter) {
  const terms = normalizeSoloSearch(query).split(/\s+/).filter(Boolean);

  return affixes.filter((affix) => {
    if (rarity !== "all" && affix.rarity !== rarity) return false;
    const content = normalizeSoloSearch([affix.id, affix.name, affix.description, ...affix.details].join(" "));
    return terms.every((term) => content.includes(term));
  });
}
