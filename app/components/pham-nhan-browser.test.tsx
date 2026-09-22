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
