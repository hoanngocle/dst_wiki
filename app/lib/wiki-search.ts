import type {
  CatalogSummary,
  ItemAvailabilityFilter,
  ItemListEntry,
  ItemSourceFilter,
  PrefabCategoryFilter,
} from "./item-catalog";

export type GameCategory =
  | "survival"
  | "food-farming"
  | "combat-equipment"
  | "crafting-resources"
  | "structures-decor"
  | "magic-exploration"
  | "creatures";
export type GameCategoryFilter = "all" | GameCategory;
export type CatalogCategoryFilter = PrefabCategoryFilter | GameCategory;

export const GAME_CATEGORY_OPTIONS: readonly {
  value: GameCategoryFilter;
  label: string;
}[] = [
  { value: "all", label: "Tất cả" },
  { value: "survival", label: "Sinh tồn" },
  { value: "food-farming", label: "Thức ăn & canh tác" },
  { value: "combat-equipment", label: "Chiến đấu & trang bị" },
  { value: "crafting-resources", label: "Chế tạo & tài nguyên" },
  { value: "structures-decor", label: "Công trình & trang trí" },
  { value: "magic-exploration", label: "Phép thuật & khám phá" },
  { value: "creatures", label: "Sinh vật" },
];

const GAME_CATEGORY_NAMES: Readonly<Record<GameCategory, readonly string[]>> = {
  survival: [
    "cooling", "healing", "health loss", "light sources", "survival tab",
    "tools filter", "tools tab", "warmth", "water resistant",
  ],
  "food-farming": [
    "beefalo foods", "cooking filter", "crock pot recipes", "eggs", "fertilizer",
    "fishes", "food", "food gardening filter", "food tab", "fruits", "meats",
    "monster foods", "plants", "vegetables",
  ],
  "combat-equipment": [
    "armor", "armour filter", "backpacks", "boss dropped items", "clothing filter",
    "dress tab", "equipable items", "fight tab", "hats", "melee weapons",
    "ranged weapons", "survivor items filter", "weapons",
  ],
  "crafting-resources": [
    "craftable items", "craftable items and structures on dst", "craftable structures",
    "fuel", "gems", "mineable objects", "rare blueprint exclusive", "refine tab",
    "resources", "science", "science tier 1", "science tier 2", "turf items",
  ],
  "structures-decor": [
    "containers", "crafting stations", "decorations filter", "mob housing",
    "structures", "structures filter", "structures tab", "wall",
  ],
  "magic-exploration": [
    "a new reign", "ancient tab", "ancient tier 1", "ancient tier 2",
    "celestial filter", "celestial tab", "events", "from beyond", "magic tab",
    "magic tier 1", "magic tier 2", "nightmare state indicator", "ocean", "portal",
    "seafaring filter", "shadow magic filter", "treasure hunting tab",
  ],
  creatures: [
    "animals", "birds", "boss monsters", "cave creatures", "clockwork monsters",
    "creatures", "followers", "flying creatures", "hostile creatures", "innocents",
    "mobs", "monsters", "neutral creatures", "nocturnals", "passive creatures",
    "ruins creatures", "spiders",
  ],
};

function normalizeWikiCategory(value: string): string {
  return value
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

const GAME_CATEGORY_LOOKUP: Readonly<Record<GameCategory, ReadonlySet<string>>> = {
  survival: new Set(GAME_CATEGORY_NAMES.survival.map(normalizeWikiCategory)),
  "food-farming": new Set(GAME_CATEGORY_NAMES["food-farming"].map(normalizeWikiCategory)),
  "combat-equipment": new Set(
    GAME_CATEGORY_NAMES["combat-equipment"].map(normalizeWikiCategory),
  ),
  "crafting-resources": new Set(
    GAME_CATEGORY_NAMES["crafting-resources"].map(normalizeWikiCategory),
  ),
  "structures-decor": new Set(
    GAME_CATEGORY_NAMES["structures-decor"].map(normalizeWikiCategory),
  ),
  "magic-exploration": new Set(
    GAME_CATEGORY_NAMES["magic-exploration"].map(normalizeWikiCategory),
  ),
  creatures: new Set(GAME_CATEGORY_NAMES.creatures.map(normalizeWikiCategory)),
};

function fallbackGameCategory(item: ItemListEntry): GameCategory {
  if (["mob", "boss", "character"].includes(item.category)) return "creatures";
  if (item.category === "structure") return "structures-decor";
  if (["pill", "effect", "other"].includes(item.category)) return "magic-exploration";
  return "crafting-resources";
}

export function getItemGameCategories(item: ItemListEntry): readonly GameCategory[] {
  const wikiCategories = new Set(
    (item.wiki?.categories ?? []).map(normalizeWikiCategory),
  );
  const groups = GAME_CATEGORY_OPTIONS.flatMap((option) => {
    const category = option.value;
    if (category === "all") return [];
    return [...wikiCategories].some((name) =>
      GAME_CATEGORY_LOOKUP[category].has(name),
    )
      ? [category]
      : [];
  });

  return groups.length ? groups : [fallbackGameCategory(item)];
}

function matchesCatalogCategory(
  item: ItemListEntry,
  category: CatalogCategoryFilter,
): boolean {
  if (category === "all") return true;
  if (category in prefabCategoryValues) return item.category === category;
  return getItemGameCategories(item).includes(category as GameCategory);
}

const prefabCategoryValues: Readonly<Record<Exclude<PrefabCategoryFilter, "all">, true>> = {
  item: true,
  pill: true,
  mob: true,
  boss: true,
  character: true,
  structure: true,
  effect: true,
  other: true,
};

export function countGameCategories(
  items: readonly ItemListEntry[],
): Readonly<Record<GameCategoryFilter, number>> {
  const counts: Record<GameCategoryFilter, number> = {
    all: items.length,
    survival: 0,
    "food-farming": 0,
    "combat-equipment": 0,
    "crafting-resources": 0,
    "structures-decor": 0,
    "magic-exploration": 0,
    creatures: 0,
  };
  for (const item of items) {
    for (const category of getItemGameCategories(item)) counts[category] += 1;
  }
  return counts;
}

function foldSearchText(value: string): string {
  return value.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase().replaceAll("đ", "d");
}

export function normalizeSearchText(value: string): string {
  return foldSearchText(value).trim();
}

export function findNormalizedTextMatch(
  text: string,
  query: string,
): { start: number; end: number } | null {
  const normalizedQuery = normalizeSearchText(query);
  if (!normalizedQuery) return null;

  const clusters: { value: string; start: number; end: number }[] = [];
  let offset = 0;

  for (const character of text) {
    const start = offset;
    offset += character.length;
    const previousCluster = clusters.at(-1);

    if (/\p{M}/u.test(character) && previousCluster) {
      previousCluster.value += character;
      previousCluster.end = offset;
    } else {
      clusters.push({ value: character, start, end: offset });
    }
  }

  const sourceRanges: { start: number; end: number }[] = [];
  let normalizedText = "";

  for (const cluster of clusters) {
    const normalizedCluster = foldSearchText(cluster.value);
    normalizedText += normalizedCluster;

    for (let index = 0; index < normalizedCluster.length; index += 1) {
      sourceRanges.push({ start: cluster.start, end: cluster.end });
    }
  }

  const matchIndex = normalizedText.indexOf(normalizedQuery);
  if (matchIndex < 0) return null;

  const firstRange = sourceRanges[matchIndex];
  const lastRange = sourceRanges[matchIndex + normalizedQuery.length - 1];
  if (!firstRange || !lastRange) return null;

  return { start: firstRange.start, end: lastRange.end };
}

export function filterItems(
  items: readonly ItemListEntry[],
  query: string,
  source: ItemSourceFilter,
  category: CatalogCategoryFilter,
  availability: ItemAvailabilityFilter,
): ItemListEntry[] {
  const normalizedQuery = normalizeSearchText(query);

  return items.filter((item) => {
    const matchesSource = source === "all" || item.namespace === source;
    const matchesCategory = matchesCatalogCategory(item, category);
    const matchesAvailability =
      availability === "all" ||
      (availability === "recipe" ? item.recipe !== null : item.sprite !== null);
    if (!matchesSource || !matchesCategory || !matchesAvailability) {
      return false;
    }
    if (!normalizedQuery) return true;

    const searchableText = normalizeSearchText(
      [
        item.name,
        item.englishName ?? "",
        item.prefabId,
        item.description ?? "",
        item.craftingNote ?? "",
        item.wiki?.title ?? "",
        item.wiki?.title.replaceAll("/", " ") ?? "",
        ...(item.wiki?.categories ?? []),
        ...(item.wiki?.relatedPages.map((page) => page.title) ?? []),
        ...(item.wiki?.relatedPages.map((page) => page.title.replaceAll("/", " ")) ?? []),
        ...(item.recipe?.ingredients.map((ingredient) => ingredient.name) ?? []),
      ].join(" "),
    );

    return searchableText.includes(normalizedQuery);
  });
}

export type ItemSelectionFilters = {
  query?: string;
  source?: ItemSourceFilter;
  category?: CatalogCategoryFilter;
  availability?: ItemAvailabilityFilter;
};

export type SearchableItem = ItemListEntry & { searchText: string };

function itemSearchText(item: ItemListEntry): string {
  return [
    item.name,
    item.englishName ?? "",
    item.prefabId,
    item.description ?? "",
    item.craftingNote ?? "",
    item.wiki?.title ?? "",
    ...(item.wiki?.categories ?? []),
    ...(item.wiki?.relatedPages.map((page) => page.title) ?? []),
    ...(item.recipe?.ingredients.map((ingredient) => ingredient.name) ?? []),
  ].join(" ");
}

export function selectItems(
  items: readonly ItemListEntry[],
  filters: ItemSelectionFilters = {},
): SearchableItem[] {
  const selected = filterItems(
    items,
    filters.query ?? "",
    filters.source ?? "all",
    filters.category ?? "all",
    filters.availability ?? "all",
  );

  return selected.map((item) => ({ ...item, searchText: itemSearchText(item) }));
}

export function hasRealPrefab(item: ItemListEntry): boolean {
  return item.wiki?.mappingState !== "unmatched";
}

export function summarizeItems(items: readonly ItemListEntry[]): CatalogSummary {
  return items.reduce<CatalogSummary>(
    (summary, item) => ({
      total: summary.total + 1,
      wiki: summary.wiki + Number(item.wiki !== null),
      recipes: summary.recipes + Number(item.recipe !== null),
      pictured: summary.pictured + Number(item.sprite !== null),
    }),
    { total: 0, wiki: 0, recipes: 0, pictured: 0 },
  );
}
