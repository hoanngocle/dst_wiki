import { describe, expect, it } from "vitest";

import type { ItemListEntry } from "./item-catalog";
import {
  filterItems,
  findNormalizedTextMatch,
  hasRealPrefab,
  normalizeSearchText,
  summarizeItems,
} from "./wiki-search";

describe("normalizeSearchText", () => {
  it("normalizes case and surrounding whitespace", () => {
    expect(normalizeSearchText("  Ancient Blade  ")).toBe("ancient blade");
  });

  it("removes combining diacritics", () => {
    expect(normalizeSearchText("Café Ruins")).toBe("cafe ruins");
  });

  it("folds Vietnamese d with stroke", () => {
    expect(normalizeSearchText("Đèn Dẫn Lối")).toBe("den dan loi");
  });
});

describe("findNormalizedTextMatch", () => {
  it.each([
    ["Đèn Dẫn Lối", "den", { start: 0, end: 3 }],
    ["Thắp đèn", "den", { start: 5, end: 8 }],
  ])("maps %s back to the original source range", (text, query, expectedRange) => {
    expect(findNormalizedTextMatch(text, query)).toEqual(expectedRange);
  });
});

const items: readonly ItemListEntry[] = [
  {
    id: "tu_tien:xd_sword",
    prefabId: "xd_sword",
    namespace: "tu_tien",
    category: "item",
    name: "Kiếm Thử",
    englishName: "Test Sword",
    description: "Một thanh kiếm từ phương bắc.",
    craftingNote: "Rèn bằng linh lực tinh khiết.",
    sprite: null,
    recipe: {
      outputCount: 1,
      ingredients: [
        {
          id: "base_game:goldnugget",
          name: "Vàng",
          amount: 2,
          sprite: null,
        },
      ],
    },
    wiki: null,
  },
  {
    id: "base_game:goldnugget",
    prefabId: "goldnugget",
    namespace: "base_game",
    category: "item",
    name: "Vàng",
    englishName: "Gold Nugget",
    description: "Kim loại quý.",
    craftingNote: null,
    sprite: null,
    recipe: null,
    wiki: {
      pageId: 501,
      title: "Gold Nugget/DST",
      canonicalUrl: "https://dontstarve.wiki.gg/wiki/Gold_Nugget/DST",
      categories: ["Resources"],
      mappingState: "mapped",
      detailUrl: "/data/wiki/pages/501.json",
      relatedPages: [
        {
          pageId: 502,
          title: "Gold Nugget",
          canonicalUrl: "https://dontstarve.wiki.gg/wiki/Gold_Nugget",
          detailUrl: "/data/wiki/pages/502.json",
        },
      ],
    },
  },
  {
    id: "base_game:log",
    prefabId: "log",
    namespace: "base_game",
    category: "item",
    name: "Gỗ",
    englishName: "Log",
    description: "Nguyên liệu cơ bản.",
    craftingNote: null,
    sprite: {
      src: "/assets/game/log.png",
      uv: { u1: 0, u2: 1, v1: 0, v2: 1 },
    },
    recipe: null,
    wiki: null,
  },
  {
    id: "base_game:deerclops",
    prefabId: "deerclops",
    namespace: "base_game",
    category: "boss",
    name: "Deerclops",
    englishName: "Deerclops",
    description: "Một boss khổng lồ.",
    craftingNote: null,
    sprite: null,
    recipe: null,
    wiki: null,
  },
  {
    id: "wiki:100736",
    prefabId: "wiki-100736",
    namespace: "base_game",
    category: "item",
    name: "Halberd",
    englishName: "Halberd",
    description: "Pointy and hurty.",
    craftingNote: null,
    sprite: null,
    recipe: null,
    wiki: {
      pageId: 100736,
      title: "Halberd",
      canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd",
      categories: ["Ancient Weapons"],
      mappingState: "unmatched",
      detailUrl: "/data/wiki/pages/100736.json",
      relatedPages: [],
    },
  },
];

describe("filterItems", () => {
  it("preserves all items for an empty query and all filter", () => {
    expect(filterItems(items, "", "all", "all", "all")).toEqual(items);
  });

  it.each([
    "kiem",
    "test sword",
    "xd_sword",
    "phuong bac",
    "vang",
    "linh luc tinh khiet",
    "gold nugget dst",
    "ancient weapons",
    "gold nugget",
  ])(
    "matches the real searchable field %s",
    (query) => {
      const resultIds = filterItems(items, query, "all", "all", "all").map(
        (item) => item.id,
      );
      expect(resultIds.length).toBeGreaterThan(0);
    },
  );

  it("groups every Wiki-backed DST record under DST", () => {
    expect(
      filterItems(items, "", "base_game", "all", "all").map((item) => item.id),
    ).toEqual([
      "base_game:goldnugget",
      "base_game:log",
      "base_game:deerclops",
      "wiki:100736",
    ]);
    expect(
      filterItems(items, "", "tu_tien", "all", "all").map((item) => item.id),
    ).toEqual(["tu_tien:xd_sword"]);
  });

  it("combines source and text filters", () => {
    expect(
      filterItems(items, "kiem", "tu_tien", "all", "all").map((item) => item.id),
    ).toEqual(["tu_tien:xd_sword"]);
    expect(filterItems(items, "kiem", "base_game", "all", "all")).toEqual([]);
  });

  it("filters by recipe and image availability", () => {
    expect(
      filterItems(items, "", "all", "all", "recipe").map((item) => item.id),
    ).toEqual(["tu_tien:xd_sword"]);
    expect(
      filterItems(items, "", "all", "all", "image").map((item) => item.id),
    ).toEqual(["base_game:log"]);
  });

  it("combines source and prefab category filters", () => {
    expect(
      filterItems(items, "", "base_game", "boss", "all").map((item) => item.id),
    ).toEqual(["base_game:deerclops"]);
    expect(filterItems(items, "", "tu_tien", "boss", "all")).toEqual([]);
  });
});

describe("catalog presentation semantics", () => {
  it("summarizes real data availability", () => {
    expect(summarizeItems(items)).toEqual({
      total: 5,
      wiki: 2,
      recipes: 1,
      pictured: 1,
    });
  });

  it("distinguishes mapped entities from standalone wiki pages", () => {
    expect(hasRealPrefab(items[1])).toBe(true);
    expect(hasRealPrefab(items[4])).toBe(false);
  });
});
