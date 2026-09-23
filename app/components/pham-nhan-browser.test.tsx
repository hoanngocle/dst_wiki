import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { PhamNhanBrowser } from "./pham-nhan-browser";
import type { PhamNhanSnapshot } from "@/app/lib/pham-nhan";

const data: PhamNhanSnapshot = { meta: { name: "Phàm Nhân", version: "2.0" }, items: [{ id: "item:stone", prefab: "stone", name: "Hạ Phẩm Linh Thạch", sprite: null, category: "material", description: "Rơi từ mỏ", details: [], recipeStatus: "none", recipes: [], acquisition: [{ text: "Mỏ" }], relatedIds: [] }, { id: "item:scroll", prefab: "scroll", name: "Tầm Bảo Quyển Trục", sprite: null, category: "blueprint-token", description: "Hai công thức", details: [], recipeStatus: "known", recipes: [{ id: "a", kind: "crafting", product: "scroll", amount: 1, ingredients: [], station: "MAGIC", conditions: [] }, { id: "b", kind: "crafting", product: "scroll", amount: 1, ingredients: [], station: "MAGIC", conditions: [] }], acquisition: [], relatedIds: [] }], affixes: [], guides: [], config: [] };

it("searches Vietnamese without accents and opens an item dialog", () => {
  render(<PhamNhanBrowser data={data} />);
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm trong Phàm Nhân" }), { target: { value: "ha pham linh thach" } });
  expect(screen.getByText("Hạ Phẩm Linh Thạch")).toBeDefined();
  fireEvent.click(screen.getByText("Hạ Phẩm Linh Thạch"));
  expect(screen.getByRole("dialog", { name: "Hạ Phẩm Linh Thạch" })).toBeDefined();
  fireEvent.keyDown(screen.getByRole("dialog"), { key: "Escape" });
  expect(screen.queryByRole("dialog")).toBeNull();
});

it("returns to the first page when the search changes", () => {
  const paginatedData: PhamNhanSnapshot = {
    ...data,
    items: Array.from({ length: 13 }, (_, index) => ({
      ...data.items[0],
      id: `item:${index + 1}`,
      prefab: `item_${index + 1}`,
      name: `Vật phẩm ${index + 1}`,
    })),
  };

  render(<PhamNhanBrowser data={paginatedData} />);
  fireEvent.click(screen.getByRole("button", { name: "Sau →" }));
  expect(screen.getByText("Trang 2 / 2")).toBeDefined();

  const search = screen.getByRole("searchbox", { name: "Tìm trong Phàm Nhân" });
  fireEvent.change(search, { target: { value: "vat pham 13" } });
  fireEvent.change(search, { target: { value: "" } });

  expect(screen.getByText("Trang 1 / 2")).toBeDefined();
});
