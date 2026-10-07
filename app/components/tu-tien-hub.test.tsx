import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import { TuTienHub } from "./tu-tien-hub";
import modSnapshot from "@/data/generated/tu-tien-mods.json";
import spriteSnapshot from "@/data/generated/tu-tien-mod-sprites.json";

it("keeps all 36 Nyx appearances in Nyx without a separate clothing tab", () => {
  window.history.replaceState(null, "", "/tu-tien#nyx");
  render(<TuTienHub crafting={null} cultivation={null} mods={modSnapshot.mods} referenceItems={[]} sprites={{}} />);
  expect(screen.queryByRole("tab", { name: "Trang Phục" })).toBeNull();
  fireEvent.change(screen.getByRole("combobox", { name: "Nhóm nội dung Nyx" }), { target: { value: "Ngoại hình" } });
  expect(screen.getByRole("status").textContent).toContain("36 /");
  expect(screen.getAllByRole("heading", { level: 3 })).toHaveLength(36);
  expect(screen.queryByRole("button", { name: "Sau" })).toBeNull();
  expect(screen.getByRole("heading", { name: "Vân Tiêu · xd_yunxiao_zwzy" })).toBeDefined();
});


it("opens the building guide and price tables from the Công Trình tab", () => {
  window.history.replaceState(null, "", "/tu-tien#cong-trinh");
  render(<TuTienHub crafting={null} cultivation={null} mods={modSnapshot.mods} referenceItems={[]} sprites={{}} />);
  expect(screen.getByRole("tab", { name: "Công Trình" }).getAttribute("aria-selected")).toBe("true");
  expect(screen.getByRole("heading", { level: 2, name: "Công Trình" })).toBeDefined();
  expect(screen.getByRole("table", { name: "Bảng giá nền Máy Tái Luyện" })).toBeDefined();
  expect(screen.getByRole("table", { name: "Tỷ lệ nhóm kho báu" })).toBeDefined();
});


it("shows all Thần Khí gems in a searchable table with their source icons", () => {
  window.history.replaceState(null, "", "/tu-tien#than-khi");
  render(<TuTienHub crafting={null} cultivation={null} mods={modSnapshot.mods} referenceItems={[]} sprites={spriteSnapshot.sprites} />);
  const filter = screen.getByRole("combobox", { name: "Nhóm nội dung Thần Khí Tu Tiên" });
  expect(within(filter).getByRole("option", { name: "Đá Quý" })).toBeDefined();
  fireEvent.change(filter, { target: { value: "Đá thuộc tính" } });
  const table = screen.getByRole("table", { name: "Bảng Đá Quý" });
  expect(within(table).getAllByRole("row")).toHaveLength(79);
  expect(within(table).getAllByTestId("game-sprite")).toHaveLength(78);
  expect(within(table).getByRole("row", { name: /Nhanh Nhẹn I.*Vũ khí.*1-5%.*60%/ })).toBeDefined();
  expect(screen.queryByRole("button", { name: "Sau" })).toBeNull();
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm trong Thần Khí Tu Tiên" }), { target: { value: "tu linh" } });
  expect(within(table).getAllByRole("row")).toHaveLength(11);
});
