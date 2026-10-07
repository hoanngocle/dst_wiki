import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import data from "@/data/generated/tu-tien-structures.json";
import { TuTienStructures } from "./tu-tien-structures";

it("shows the recycler recipe, instructions and base price table", () => {
  render(<TuTienStructures referenceItems={[]} sprites={{}} />);
  fireEvent.change(screen.getByRole("combobox", { name: "Nhóm công trình" }), { target: { value: "Máy Tái Luyện" } });
  expect(screen.getByRole("heading", { name: "Máy Tái Luyện" })).toBeDefined();
  expect(screen.getByLabelText(`${data.names.cutstone}, số lượng 4`)).toBeDefined();
  expect(screen.getByText(/Xác nhận.*8 giây/)).toBeDefined();
  const prices = screen.getByRole("table", { name: "Bảng giá nền Máy Tái Luyện" });
  expect(within(prices).getByText(data.names.smallmeat).closest("tr")?.textContent).toBeDefined();
  expect(within(prices).getByText(data.names.xd_qlr).closest("tr")?.textContent).toContain("200");
});

it("shows both scroll recipes and normalized group and per-outcome rates", () => {
  render(<TuTienStructures referenceItems={[]} sprites={{}} />);
  fireEvent.change(screen.getByRole("combobox", { name: "Nhóm công trình" }), { target: { value: "Kho báu" } });
  expect(screen.getByLabelText(`${data.names.stinger}, số lượng 40`)).toBeDefined();
  expect(screen.getByLabelText(`${data.names.silk}, số lượng 40`)).toBeDefined();
  expect(screen.getByLabelText(`${data.names.spidergland}, số lượng 20`)).toBeDefined();
  const groups = screen.getByRole("table", { name: "Tỷ lệ nhóm kho báu" });
  expect(within(groups).getByRole("row", { name: /Thông thường.*35.*33,3333%/ })).toBeDefined();
  const common = screen.getByRole("table", { name: "Vật phẩm kho báu Thông thường" });
  expect(within(common).getByText(data.names.amulet).closest("tr")?.textContent).toContain("1,7857%0,5952%");
  expect(screen.getByText(/chỉ tính các prefab có sẵn/i)).toBeDefined();
});

it("lists building and item recipes, output quantities and use instructions", () => {
  render(<TuTienStructures referenceItems={[]} sprites={{}} />);
  expect(screen.getByRole("heading", { name: "Bếp Thần Hỏa" })).toBeDefined();
  expect(screen.getByRole("heading", { name: "Thiên Nghịch Châu" })).toBeDefined();
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm công trình và vật phẩm" }), { target: { value: "Thảm Da Báo" } });
  expect(screen.getByRole("heading", { name: "Thảm Da Báo" })).toBeDefined();
  expect(screen.getByText(/Nhận được: 4/)).toBeDefined();
  expect(screen.getByText(/Chọn thảm.*đặt lên nền/)).toBeDefined();
});


it("normalizes rates, combines duplicate outcomes and keeps complete recipe quantities", () => {
  const weights = data.treasureGroups.reduce((sum, group) => sum + group.weight, 0);
  expect(weights).toBe(105);
  const rates = new Map<string, number>();
  for (const group of data.treasureGroups) {
    for (const prefab of group.prefabs) rates.set(prefab, (rates.get(prefab) ?? 0) + group.weight / weights / group.prefabs.length);
  }
  expect([...rates.values()].reduce((sum, rate) => sum + rate, 0)).toBeCloseTo(1, 10);
  expect(rates.get("amulet")).toBeCloseTo(35 / 105 / 56 + 15 / 105 / 33, 10);
  expect(data.entries.every(entry => entry.recipes.length > 0 && entry.usage.length > 0)).toBe(true);
  expect(data.entries.filter(entry => entry.group === "Thảm")).toHaveLength(15);
  expect(data.entries.find(entry => entry.prefab === "homesign")!.recipes[0]).toMatchObject({ technology: "Máy Khoa Học", ingredients: [{ prefab: "boards", amount: 1 }] });
  expect(data.entries.find(entry => entry.prefab === "deluxe_firepit")!.recipes[0].ingredients).toEqual([{ prefab: "log", amount: 6 }, { prefab: "goldnugget", amount: 3 }, { prefab: "cutstone", amount: 14 }]);
});
