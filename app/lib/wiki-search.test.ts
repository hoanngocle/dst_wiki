import { describe, expect, it } from "vitest";

import type { ItemListEntry } from "./item-catalog";
import {
  filterItems,
  findNormalizedTextMatch,
  normalizeSearchText,
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
  },
  {
    id: "base_game:log",
    prefabId: "log",
    namespace: "base_game",
    category: "item",
    name: "Gỗ",
    englishName: "Log",
    description: "Nguyên liệu cơ bản.",
    sprite: null,
    recipe: null,
  },
  {
    id: "base_game:deerclops",
    prefabId: "deerclops",
    namespace: "base_game",
    category: "boss",
    name: "Deerclops",
    englishName: "Deerclops",
    description: "Một boss khổng lồ.",
    sprite: null,
    recipe: null,
  },
];

describe("filterItems", () => {
  it("preserves all items for an empty query and all filter", () => {
    expect(filterItems(items, "", "all", "all")).toEqual(items);
  });

  it.each(["kiem", "test sword", "xd_sword", "phuong bac", "vang"])(
    "matches the real searchable field %s",
    (query) => {
      expect(filterItems(items, query, "all", "all").map((item) => item.id)).toEqual([
        "tu_tien:xd_sword",
      ]);
    },
  );

  it("combines namespace and text filters", () => {
    expect(filterItems(items, "kiem", "tu_tien", "all").map((item) => item.id)).toEqual([
      "tu_tien:xd_sword",
    ]);
    expect(filterItems(items, "kiem", "base_game", "all")).toEqual([]);
  });

  it("filters craftable items", () => {
    expect(filterItems(items, "", "craftable", "all").map((item) => item.id)).toEqual([
      "tu_tien:xd_sword",
    ]);
  });

  it("combines namespace and prefab category filters", () => {
    expect(
      filterItems(items, "", "base_game", "boss").map((item) => item.id),
    ).toEqual(["base_game:deerclops"]);
    expect(filterItems(items, "", "tu_tien", "boss")).toEqual([]);
  });

});
