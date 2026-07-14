import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ItemRecipe } from "@/app/lib/item-catalog";
import { RecipeIngredients } from "./recipe-ingredients";

describe("RecipeIngredients", () => {
  it("renders ingredient images multiplied by integer quantities", () => {
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

    render(<RecipeIngredients recipe={recipe} />);

    expect(screen.getByLabelText("Vàng, số lượng 2")).toBeDefined();
    expect(screen.getByText("×2")).toBeDefined();
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
