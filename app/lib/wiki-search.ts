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

export function normalizeSearchText(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();
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
