import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { ItemResult } from "./item-result";

const item: ItemListEntry = {
  id: "tu_tien:xd_sword",
  prefabId: "xd_sword",
  namespace: "tu_tien",
  category: "item",
  name: "Kiếm Thử",
  englishName: "Test Sword",
  description: "Một thanh kiếm",
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
};

const ingredientItem: ItemListEntry = {
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

describe("ItemResult", () => {
  it("renders the item identity, source, image, and recipe", () => {
    render(<ItemResult item={item} query="" />);

    expect(screen.getByRole("heading", { name: "Kiếm Thử" })).toBeDefined();
    expect(screen.getByText("Tu Tiên")).toBeDefined();
    expect(screen.getByText("xd_sword")).toBeDefined();
    expect(screen.getByLabelText("Loại: Item")).toBeDefined();
    expect(screen.getByText("×2")).toBeDefined();
  });

  it("renders the localized prefab category", () => {
    render(<ItemResult item={{ ...item, category: "boss" }} query="" />);

    expect(screen.getByLabelText("Loại: Boss")).toBeDefined();
    expect(screen.getByText("Boss")).toBeDefined();
  });

  it("highlights a normalized Vietnamese name match", () => {
    render(<ItemResult item={item} query="kiem" />);

    expect(screen.getByText("Kiếm").tagName).toBe("MARK");
  });

  it("labels referenced base-game dependencies accurately", () => {
    render(
      <ItemResult
        item={{ ...item, id: "base_game:log", prefabId: "log", namespace: "base_game" }}
        query=""
      />,
    );

    expect(screen.getByText("DST")).toBeDefined();
    expect(screen.queryByText("DST gốc liên quan")).toBeNull();
  });

  it("shows an available English name below Vietnamese and omits an empty subtitle", () => {
    const { container, rerender } = render(<ItemResult item={item} query="" />);
    const vietnameseHeading = screen.getByRole("heading", { name: "Kiếm Thử" });
    const englishName = screen.getByText("Test Sword");

    expect(vietnameseHeading.nextElementSibling).toBe(englishName);
    expect(englishName.getAttribute("lang")).toBe("en");

    rerender(<ItemResult item={{ ...item, englishName: null }} query="" />);
    expect(container.querySelector('[lang="en"]')).toBeNull();
  });

  it("forwards the result item when its identity is clicked", () => {
    const onSelectItem = vi.fn();
    render(<ItemResult item={item} query="" onSelectItem={onSelectItem} />);

    const resultButton = screen.getByRole("button", { name: "Xem chi tiết Kiếm Thử" });
    expect(resultButton.className).toContain("cursor-pointer");
    fireEvent.click(resultButton);

    expect(onSelectItem).toHaveBeenCalledWith(item);
  });

  it("forwards the selected full ingredient item", () => {
    const onSelectItem = vi.fn();
    render(
      <ItemResult
        item={item}
        query=""
        itemsById={new Map([[ingredientItem.id, ingredientItem]])}
        onSelectItem={onSelectItem}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Vàng, số lượng 2" }));
    expect(onSelectItem).toHaveBeenCalledWith(ingredientItem);
  });
});
