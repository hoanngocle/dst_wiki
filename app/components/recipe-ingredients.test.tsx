import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ItemListEntry, ItemRecipe } from "@/app/lib/item-catalog";
import { RecipeIngredients } from "./recipe-ingredients";

const recipe: ItemRecipe = {
  outputCount: 1,
  ingredients: [
    {
      id: "base_game:goldnugget",
      name: "Vàng",
      amount: 2,
      sprite: null,
    },
  ],
};

const fullItem: ItemListEntry = {
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

describe("RecipeIngredients", () => {
  it("renders ingredient images multiplied by integer quantities", () => {
    render(<RecipeIngredients recipe={recipe} />);

    expect(screen.getByLabelText("Vàng, số lượng 2")).toBeDefined();
    expect(screen.getByText("×2")).toBeDefined();
  });

  it("shows a linked tooltip and emits the referenced full item", () => {
    const onSelectItem = vi.fn();

    render(
      <RecipeIngredients
        recipe={recipe}
        itemsById={new Map([[fullItem.id, fullItem]])}
        onSelectItem={onSelectItem}
      />,
    );

    const ingredient = screen.getByRole("button", { name: "Vàng, số lượng 2" });
    const tooltip = screen.getByRole("tooltip", { name: "Vàng" });
    expect(ingredient.getAttribute("aria-describedby")).toBe(tooltip.id);
    expect(ingredient.className).toContain("cursor-pointer");

    fireEvent.click(ingredient);
    expect(onSelectItem).toHaveBeenCalledWith(fullItem);
  });

  it("keeps unresolved ingredients non-interactive", () => {
    render(
      <RecipeIngredients recipe={recipe} itemsById={new Map()} onSelectItem={vi.fn()} />,
    );

    expect(screen.queryByRole("button", { name: "Vàng, số lượng 2" })).toBeNull();
    expect(screen.getByLabelText("Vàng, số lượng 2")).toBeDefined();
  });

  it("shows an explicit state when an item has no recipe", () => {
    render(<RecipeIngredients recipe={null} />);

    expect(screen.getByText("Không có công thức")).toBeDefined();
  });

  it("distinguishes special recipes with no normal ingredients", () => {
    render(<RecipeIngredients recipe={{ outputCount: 1, ingredients: [] }} />);

    expect(screen.getByText("Công thức đặc biệt")).toBeDefined();
  });
});
