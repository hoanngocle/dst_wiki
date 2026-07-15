import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

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
  }));
}

describe("WikiSearch", () => {
  it("shows every item before the user filters", () => {
    render(<WikiSearch items={items} />);
    expect(screen.getByText("Kiếm Thử")).toBeDefined();
    expect(screen.getByText("Gỗ")).toBeDefined();
    expect(screen.getByText("2 Prefabs")).toBeDefined();
  });

  it("filters immediately as the user types without requiring diacritics", () => {
    render(<WikiSearch items={items} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." }), {
      target: { value: "kiem" },
    });
    expect(screen.getByText("Kiếm Thử")).toBeDefined();
    expect(screen.queryByText("Gỗ")).toBeNull();
    expect(screen.getByText("1 Prefab")).toBeDefined();
  });

  it("announces result context when equal-count result sets change", () => {
    render(<WikiSearch items={items} />);
    const search = screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." });

    fireEvent.change(search, { target: { value: "kiem" } });
    const status = screen.getByRole("status");
    expect(status.textContent).toBe(
      '1 Prefab khớp với "kiem" trong Tất cả, Tất cả loại.',
    );

    fireEvent.change(search, { target: { value: "go" } });
    expect(status.textContent).toBe(
      '1 Prefab khớp với "go" trong Tất cả, Tất cả loại.',
    );
  });

  it("filters by namespace and craftability", () => {
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

  it("combines category and namespace filters", () => {
    render(<WikiSearch items={items} />);

    expect(screen.getByRole("group", { name: "Lọc theo category" })).toBeDefined();
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

  it("exposes item filters as a named group", () => {
    render(<WikiSearch items={items} />);
    expect(screen.getByRole("group", { name: "Lọc Prefabs" })).toBeDefined();
  });

  it("clears query and filter from the empty state", () => {
    render(<WikiSearch items={items} />);
    fireEvent.click(screen.getByRole("button", { name: "DST" }));
    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." }), {
      target: { value: "kiem" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Xóa bộ lọc" }));
    expect(screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." })).toHaveProperty(
      "value",
      "",
    );
    expect(screen.getByRole("button", { name: "Tất cả" }).getAttribute("aria-pressed")).toBe(
      "true",
    );
  });

  it("highlights matching text", () => {
    render(<WikiSearch items={items} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." }), {
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
    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." }), {
      target: { value: "cafe" },
    });

    expect(document.querySelector("mark")?.textContent).toBe("Cafe\u0301");
  });

  it("restarts result-boundary motion when filtering retains keyed cards", () => {
    render(<WikiSearch items={items} />);
    const firstBoundary = screen.getByRole("list");

    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." }), {
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
    const search = screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." });
    fireEvent.change(search, { target: { value: "kiem" } });
    const clear = screen.getByRole("button", { name: "Xóa tìm kiếm" });
    clear.focus();
    fireEvent.click(clear);
    expect(search).toHaveProperty("value", "");
    expect(document.activeElement).toBe(search);
  });

  it("keeps the clear search touch target at least 44px tall", () => {
    render(<WikiSearch items={items} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." }), {
      target: { value: "kiem" },
    });

    expect(screen.getByRole("button", { name: "Xóa tìm kiếm" }).className).toContain(
      "min-h-11",
    );
  });

  it("focuses search with slash and Control K", () => {
    render(<WikiSearch items={items} />);
    const search = screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." });
    fireEvent.keyDown(window, { key: "/" });
    expect(document.activeElement).toBe(search);

    document.body.focus();
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    expect(document.activeElement).toBe(search);
  });

  it("clears the query with Escape", () => {
    render(<WikiSearch items={items} />);
    const search = screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." });
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

    fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." }), {
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
    expect(within(dialog).getByText("Prefab ID")).toBeDefined();

    fireEvent.click(within(dialog).getByRole("button", { name: "Đóng chi tiết" }));
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(ingredient);
  });
});
