import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import Page from "@/app/pham-nhan-tu-tien/tien-trinh/page";

it("publishes integrated progression with complete totals and active navigation", () => {
  render(<Page />);
  expect(screen.getByRole("heading", { level: 1, name: "Tiến trình Phàm Nhân Tu Tiên" })).toBeDefined();
  const nav = screen.getByRole("link", { name: "Tiến trình" });
  expect(nav.getAttribute("href")).toBe("/pham-nhan-tu-tien/tien-trinh");
  expect(nav.getAttribute("aria-current")).toBe("page");
  expect(screen.queryByRole("link", { name: "Achievement & Level" })).toBeNull();
  const stats = screen.getByLabelText("Tổng quan tiến trình");
  for (const value of ["231", "13", "1000", "39", "945"]) expect(within(stats).getByText(value)).toBeDefined();
  expect(screen.getByRole("heading", { name: "15 đan tu luyện" })).toBeDefined();
  expect(screen.getByRole("heading", { name: "10 đan buff" })).toBeDefined();
  expect(within(screen.getByRole("table", { name: "Hạng nhân vật" })).getByRole("row", { name: "SS 70" })).toBeDefined();
  expect(within(screen.getByRole("table", { name: "Hạng nhân vật" })).getByRole("row", { name: "SSS 100" })).toBeDefined();
});

it("lets readers search achievements without losing seasonal rewards", () => {
  render(<Page />);
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm thành tựu" }), { target: { value: "food_meatballs" } });
  const table = screen.getByRole("table", { name: "Thành tựu" });
  expect(within(table).getAllByRole("row")).toHaveLength(2);
  expect(within(table).getByText("Viên Thịt")).toBeDefined();
  expect(screen.getAllByText("20 nhiệm vụ mỗi mùa: 16 một lần + 4 lặp lại")).toHaveLength(4);
  expect(screen.getByText(/goose_feather × 1/)).toBeDefined();
  expect(screen.getByText(/deerclops_eyeball × 1/)).toBeDefined();
});
