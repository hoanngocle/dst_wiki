import type {
  CatalogSummary,
  ItemAvailabilityFilter,
  ItemListEntry,
  ItemSourceFilter,
  PrefabCategoryFilter,
} from "./item-catalog";

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
  category: PrefabCategoryFilter,
  availability: ItemAvailabilityFilter,
): ItemListEntry[] {
  const normalizedQuery = normalizeSearchText(query);

  return items.filter((item) => {
    const matchesSource =
      source === "all" ||
      (source === "wiki"
        ? item.wiki !== null
        : item.namespace === source && item.wiki === null);
    const matchesCategory = category === "all" || item.category === category;
    const matchesAvailability =
      availability === "all" ||
      (availability === "recipe" ? item.recipe !== null : item.sprite !== null);
    if (!matchesSource || !matchesCategory || !matchesAvailability) return false;
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
