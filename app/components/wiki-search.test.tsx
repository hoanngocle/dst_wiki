import { fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { WikiSearch } from "./wiki-search";

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
    id: "base_game:log",
    prefabId: "log",
    namespace: "base_game",
    category: "structure",
    name: "Gỗ",
    englishName: "Log",
    description: "Nguyên liệu cơ bản.",
    craftingNote: null,
    sprite: null,
    recipe: null,
    wiki: null,
  },
];

const goldItem: ItemListEntry = {
  id: "base_game:goldnugget",
  prefabId: "goldnugget",
  namespace: "base_game",
  category: "item",
  name: "Vàng",
  englishName: "Gold Nugget",
  description: "Một cục vàng.",
  craftingNote: null,
  sprite: null,
  recipe: null,
  wiki: null,
};

const wikiItem: ItemListEntry = {
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
    categories: ["Items"],
    mappingState: "unmatched",
    detailUrl: "/data/wiki/pages/100736.json",
    relatedPages: [],
  },
};

function makeItems(count: number): ItemListEntry[] {
  return Array.from({ length: count }, (_, index) => ({
    id: `tu_tien:item_${index + 1}`,
    prefabId: `item_${index + 1}`,
    namespace: "tu_tien" as const,
    category: "other" as const,
    name: `Mục ${index + 1}`,
    englishName: null,
    description: null,
    craftingNote: null,
    sprite: null,
    recipe: null,
    wiki: null,
  }));
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("WikiSearch", () => {
  it("shows every item before the user filters", () => {
    render(<WikiSearch items={items} />);
    expect(screen.getByText("Kiếm Thử")).toBeDefined();
    expect(screen.getByText("Gỗ")).toBeDefined();
    expect(screen.getByText("2 vật phẩm")).toBeDefined();
  });

  it("filters immediately as the user types without requiring diacritics", () => {
    render(<WikiSearch items={items} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), {
      target: { value: "kiem" },
    });
    expect(screen.getByText("Kiếm Thử")).toBeDefined();
    expect(screen.queryByText("Gỗ")).toBeNull();
    expect(screen.getByText("1 vật phẩm")).toBeDefined();
  });

  it("announces result context when equal-count result sets change", () => {
    render(<WikiSearch items={items} />);
    const search = screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." });

    fireEvent.change(search, { target: { value: "kiem" } });
    const status = screen.getByRole("status");
    expect(status.textContent).toBe(
      '1 vật phẩm khớp với "kiem" trong Tất cả, Tất cả loại, Tất cả dữ liệu.',
    );

    fireEvent.change(search, { target: { value: "go" } });
    expect(status.textContent).toBe(
      '1 vật phẩm khớp với "go" trong Tất cả, Tất cả loại, Tất cả dữ liệu.',
    );
  });

  it("filters by source and data availability", () => {
    render(<WikiSearch items={items} />);
    const namespaceFilter = screen.getByRole("button", { name: "Tu Tiên" });
    expect(namespaceFilter.className).toContain("cursor-pointer");
    fireEvent.click(namespaceFilter);
    expect(screen.getByText("Kiếm Thử")).toBeDefined();
    expect(screen.queryByText("Gỗ")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Có công thức" }));
    expect(screen.getByText("Kiếm Thử")).toBeDefined();
    expect(screen.queryByText("Gỗ")).toBeNull();
  });

  it("filters standalone wiki items without treating them as DST prefabs", () => {
    render(<WikiSearch items={[...items, wikiItem]} />);

    fireEvent.click(screen.getByRole("button", { name: "Wiki" }));
    expect(screen.getByRole("heading", { name: "Halberd" })).toBeDefined();
    expect(screen.queryByText("Kiếm Thử")).toBeNull();
    expect(screen.queryByText("Gỗ")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Có công thức" }));
    expect(screen.queryByRole("heading", { name: "Halberd" })).toBeNull();
  });

  it("combines category and namespace filters", () => {
    render(<WikiSearch items={items} />);

    expect(screen.getByRole("group", { name: "Lọc theo danh mục" })).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: "Công trình" }));
    expect(screen.getByText("Gỗ")).toBeDefined();
    expect(screen.queryByText("Kiếm Thử")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Tu Tiên" }));
    expect(screen.queryByText("Gỗ")).toBeNull();
  });

  it("keeps source metadata visible and available to assistive technology", () => {
    render(<WikiSearch items={items} />);
    const swordCard = screen.getByText("Kiếm Thử").closest("li");

    expect(swordCard).not.toBeNull();
    const source = within(swordCard as HTMLElement).getByText("Tu Tiên");
    expect(source.className.split(/\s+/)).not.toContain("hidden");
    expect(swordCard?.textContent).toContain("xd_sword");
  });

  it("exposes source and availability filters as named groups", () => {
    render(<WikiSearch items={items} />);
    expect(screen.getByRole("group", { name: "Lọc theo nguồn" })).toBeDefined();
    expect(screen.getByRole("group", { name: "Lọc theo dữ liệu" })).toBeDefined();
  });

  it("clears query and filter from the empty state", () => {
    render(<WikiSearch items={items} />);
    fireEvent.click(screen.getByRole("button", { name: "DST" }));
    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), {
      target: { value: "kiem" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Xóa bộ lọc" }));
    expect(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." })).toHaveProperty(
      "value",
      "",
    );
    expect(screen.getByRole("button", { name: "Tất cả" }).getAttribute("aria-pressed")).toBe(
      "true",
    );
  });

  it("highlights matching text", () => {
    render(<WikiSearch items={items} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), {
      target: { value: "kiem" },
    });
    expect(screen.getByText("Kiếm").tagName).toBe("MARK");
  });

  it("highlights the complete original grapheme for decomposed Unicode text", () => {
    const decomposedItems: readonly ItemListEntry[] = [
      {
        ...items[0],
        id: "tu_tien:cafe_item",
        prefabId: "cafe_item",
        name: "Cafe\u0301 Item",
        englishName: null,
      },
    ];

    render(<WikiSearch items={decomposedItems} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), {
      target: { value: "cafe" },
    });

    expect(document.querySelector("mark")?.textContent).toBe("Cafe\u0301");
  });

  it("restarts result-boundary motion when filtering retains keyed cards", () => {
    render(<WikiSearch items={items} />);
    const firstBoundary = screen.getByRole("list");

    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), {
      target: { value: "kiem" },
    });

    const nextBoundary = screen.getByRole("list");
    expect(nextBoundary).not.toBe(firstBoundary);
    expect(nextBoundary.className).toContain(
      "motion-safe:animate-[atlas-result-in_180ms_ease-out]",
    );
  });

  it("returns focus to search after clearing the query", () => {
    render(<WikiSearch items={items} />);
    const search = screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." });
    fireEvent.change(search, { target: { value: "kiem" } });
    const clear = screen.getByRole("button", { name: "Xóa tìm kiếm" });
    clear.focus();
    fireEvent.click(clear);
    expect(search).toHaveProperty("value", "");
    expect(document.activeElement).toBe(search);
  });

  it("keeps the clear search touch target at least 44px tall", () => {
    render(<WikiSearch items={items} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), {
      target: { value: "kiem" },
    });

    expect(screen.getByRole("button", { name: "Xóa tìm kiếm" }).className).toContain(
      "min-h-11",
    );
  });

  it("focuses search with slash and Control K", () => {
    render(<WikiSearch items={items} />);
    const search = screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." });
    fireEvent.keyDown(window, { key: "/" });
    expect(document.activeElement).toBe(search);

    document.body.focus();
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    expect(document.activeElement).toBe(search);
  });

  it("clears the query with Escape", () => {
    render(<WikiSearch items={items} />);
    const search = screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." });
    fireEvent.change(search, { target: { value: "kiem" } });
    fireEvent.keyDown(search, { key: "Escape" });
    expect(search).toHaveProperty("value", "");
  });

  it("reveals results in batches of 40", () => {
    render(<WikiSearch items={makeItems(41)} />);

    expect(screen.getAllByRole("listitem")).toHaveLength(40);
    fireEvent.click(screen.getByRole("button", { name: "Xem thêm" }));
    expect(screen.getAllByRole("listitem")).toHaveLength(41);
  });

  it("resets the visible batch when the query changes", () => {
    render(<WikiSearch items={makeItems(81)} />);
    fireEvent.click(screen.getByRole("button", { name: "Xem thêm" }));
    expect(screen.getAllByRole("listitem")).toHaveLength(80);

    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), {
      target: { value: "Mục" },
    });

    expect(screen.getAllByRole("listitem")).toHaveLength(40);
  });

  it("resets the visible batch when the category changes", () => {
    render(<WikiSearch items={makeItems(81)} />);
    fireEvent.click(screen.getByRole("button", { name: "Xem thêm" }));
    expect(screen.getAllByRole("listitem")).toHaveLength(80);

    fireEvent.click(screen.getByRole("button", { name: "Khác" }));

    expect(screen.getAllByRole("listitem")).toHaveLength(40);
  });

  it("opens item detail when a result item is clicked", () => {
    render(<WikiSearch items={items} />);

    fireEvent.click(screen.getByRole("button", { name: "Xem chi tiết Kiếm Thử" }));

    expect(screen.getByRole("dialog", { name: "Kiếm Thử" })).toBeDefined();
  });

  it("opens the referenced full item in a shared detail modal", () => {
    render(<WikiSearch items={[...items, goldItem]} />);

    const swordCard = screen.getByText("Kiếm Thử").closest("li") as HTMLElement;
    const ingredient = within(swordCard).getByRole("button", {
      name: "Vàng, số lượng 2",
    });
    ingredient.focus();
    fireEvent.click(ingredient);

    const dialog = screen.getByRole("dialog", { name: "Vàng" });
    expect(within(dialog).getByText("Gold Nugget")).toBeDefined();
    expect(within(dialog).queryByText("Prefab ID")).toBeNull();

    fireEvent.click(within(dialog).getByRole("button", { name: "Đóng chi tiết" }));
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(ingredient);
  });

  it("switches the shared modal from a mapped Wiki Usage result", async () => {
    const nightLight: ItemListEntry = {
      ...goldItem,
      id: "base_game:nightlight",
      prefabId: "nightlight",
      category: "structure",
      name: "Đèn bóng đêm",
      englishName: "Night Light",
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          schema_version: 1,
          pageId: 100736,
          title: "Halberd",
          canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd",
          html: "<p>Remaining article.</p>",
          categories: ["Items"],
          images: [],
          revision: {
            id: 569319,
            sha1: "5bf67f6c77b1a0d0c5bb66b0ef02ccf5c04dba64",
            timestamp: "2026-07-12T08:43:43Z",
          },
          normalized: {
            schema_version: 2,
            subject: {
              title: "Nightmare Fuel",
              url: "https://dontstarve.wiki.gg/wiki/Nightmare_Fuel",
              entityId: null,
            },
            dropTable: {
              rows: [
                {
                  sources: [
                    {
                      title: "Beardling",
                      url: "https://dontstarve.wiki.gg/wiki/Beardling",
                      entityId: null,
                    },
                  ],
                  quantity: "1",
                  chance: "40%",
                  context: null,
                },
              ],
            },
            usage: {
              recipes: [
                {
                  result: {
                    title: "Night Light",
                    url: "https://dontstarve.wiki.gg/wiki/Night_Light",
                    entityId: nightLight.id,
                  },
                  resultAmount: 1,
                  subjectAmount: 2,
                  ingredients: [],
                  station: "Prestihatitator",
                  dlc: null,
                  character: null,
                  note: null,
                },
              ],
            },
          },
        }),
      }),
    );
    render(<WikiSearch items={[wikiItem, nightLight]} />);

    fireEvent.click(screen.getByRole("button", { name: "Xem chi tiết Halberd" }));
    fireEvent.click(
      await screen.findByRole("button", { name: "Đèn bóng đêm, số lượng 1" }),
    );

    expect(screen.getByRole("dialog", { name: "Đèn bóng đêm" })).toBeDefined();
  });
});
