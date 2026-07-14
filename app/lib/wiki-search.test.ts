import { describe, expect, it } from "vitest";

import type { ItemListEntry } from "./item-catalog";
import { filterItems, normalizeSearchText } from "./wiki-search";

describe("normalizeSearchText", () => {
  it("normalizes case and surrounding whitespace", () => {
    expect(normalizeSearchText("  Ancient Blade  ")).toBe("ancient blade");
  });

  it("removes combining diacritics", () => {
    expect(normalizeSearchText("Café Ruins")).toBe("cafe ruins");
  });
});

const items: readonly ItemListEntry[] = [
  {
    id: "tu_tien:xd_sword",
    prefabId: "xd_sword",
    namespace: "tu_tien",
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
    name: "Gỗ",
    englishName: "Log",
    description: "Nguyên liệu cơ bản.",
    sprite: null,
    recipe: null,
  },
];

describe("filterItems", () => {
  it("preserves all items for an empty query and all filter", () => {
    expect(filterItems(items, "", "all")).toEqual(items);
  });

  it.each(["kiem", "test sword", "xd_sword", "phuong bac", "vang"])(
    "matches the real searchable field %s",
    (query) => {
      expect(filterItems(items, query, "all").map((item) => item.id)).toEqual([
        "tu_tien:xd_sword",
      ]);
    },
  );

  it("combines namespace and text filters", () => {
    expect(filterItems(items, "kiem", "tu_tien").map((item) => item.id)).toEqual([
      "tu_tien:xd_sword",
    ]);
    expect(filterItems(items, "kiem", "base_game")).toEqual([]);
  });

  it("filters craftable items", () => {
    expect(filterItems(items, "", "craftable").map((item) => item.id)).toEqual([
      "tu_tien:xd_sword",
    ]);
  });
});
