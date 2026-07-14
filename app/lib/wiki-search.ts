export const wikiCategories = ["item", "creature", "location", "quest"] as const;

export type WikiCategory = (typeof wikiCategories)[number];
export type SearchCategory = "all" | WikiCategory;
export type WikiEntryAccent = "ice" | "moss" | "sand" | "slate";

export type WikiEntry = {
  id: string;
  name: string;
  category: WikiCategory;
  description: string;
  keywords: readonly string[];
  accent: WikiEntryAccent;
};

function foldSearchText(value: string): string {
  return value.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();
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

export function filterWikiEntries(
  entries: readonly WikiEntry[],
  query: string,
  category: SearchCategory,
): WikiEntry[] {
  const normalizedQuery = normalizeSearchText(query);

  return entries.filter((entry) => {
    const matchesCategory = category === "all" || entry.category === category;
    if (!matchesCategory) return false;
    if (!normalizedQuery) return true;

    const searchableText = normalizeSearchText(
      [entry.name, entry.description, entry.category, ...entry.keywords].join(" "),
    );

    return searchableText.includes(normalizedQuery);
  });
}
