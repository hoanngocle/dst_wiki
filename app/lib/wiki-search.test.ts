import { describe, expect, it } from "vitest";

import { normalizeSearchText } from "./wiki-search";

describe("normalizeSearchText", () => {
  it("normalizes case and surrounding whitespace", () => {
    expect(normalizeSearchText("  Ancient Blade  ")).toBe("ancient blade");
  });

  it("removes combining diacritics", () => {
    expect(normalizeSearchText("Café Ruins")).toBe("cafe ruins");
  });
});

import type { WikiEntry } from "./wiki-search";
import { filterWikiEntries } from "./wiki-search";

const entries: readonly WikiEntry[] = [
  {
    id: "ancient-blade",
    name: "Ancient Blade",
    category: "item",
    description: "A relic weapon from the northern ruins.",
    keywords: ["sword", "rare"],
    accent: "ice",
  },
  {
    id: "mire-stalker",
    name: "Mire Stalker",
    category: "creature",
    description: "A territorial beast near flooded paths.",
    keywords: ["swamp", "beast"],
    accent: "moss",
  },
];

describe("filterWikiEntries", () => {
  it("preserves all entries for an empty query and all categories", () => {
    expect(filterWikiEntries(entries, "", "all")).toEqual(entries);
  });

  it.each(["blade", "relic", "item", "sword"])(
    "matches the searchable field %s",
    (query) => {
      expect(filterWikiEntries(entries, query, "all").map((entry) => entry.id)).toEqual([
        "ancient-blade",
      ]);
    },
  );

  it("combines category and text filters", () => {
    expect(filterWikiEntries(entries, "mire", "creature").map((entry) => entry.id)).toEqual([
      "mire-stalker",
    ]);
    expect(filterWikiEntries(entries, "mire", "item")).toEqual([]);
  });
});
