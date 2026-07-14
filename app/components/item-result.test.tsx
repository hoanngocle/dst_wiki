import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { ItemResult } from "./item-result";

const item: ItemListEntry = {
  id: "tu_tien:xd_sword",
  prefabId: "xd_sword",
  namespace: "tu_tien",
  name: "Kiếm Thử",
  englishName: "Test Sword",
  description: "Một thanh kiếm",
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

    expect(screen.getByText("DST gốc liên quan")).toBeDefined();
  });
});
