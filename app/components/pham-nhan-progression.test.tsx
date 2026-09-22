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

it("shows documented runtime availability separately from the complete perk catalog", () => {
  render(<Page />);
  const table = screen.getByRole("table", { name: "Kỹ năng Star" });
  for (const id of ["trinket_owner", "icy_weed", "inherit_jingwei", "inherit_hantianzun", "inherit_wangmazi"]) {
    const row = within(table).getByText(id).closest("tr")!;
    expect(within(row).getByText("Chưa khả dụng")).toBeDefined();
  }
  for (const id of ["antique_shop", "inherit_luoshen", "inherit_sanxiao", "inherit_shiji", "inherit_sudaji"]) {
    const row = within(table).getByText(id).closest("tr")!;
    expect(within(row).getByText("Một phần")).toBeDefined();
  }
  expect(within(table).getAllByText("Đã có triển khai")).toHaveLength(29);
  expect(screen.getByText(/39 kỹ năng.*945 Star.*toàn bộ danh mục/)).toBeDefined();
});

it("explains manual XP claims, durable rollover settlement and missing configuration", () => {
  render(<Page />);
  const instructions = screen.getByLabelText("Nhận EXP nhiệm vụ mùa");
  expect(instructions.textContent).toMatch(/mỗi lần hoàn thành.*kể cả mỗi lượt lặp lại.*Claim EXP/i);
  expect(instructions.textContent).toMatch(/1 lượt nhận/);
  expect(instructions.textContent).toMatch(/EXP.*cấu hình máy chủ/);
  expect(instructions.textContent).toMatch(/chưa.*cấu hình.*chưa.*khả dụng/);
  expect(instructions.textContent).toMatch(/chuyển mùa.*tự động.*nhiệm vụ.*rương.*đủ điều kiện/i);
  expect(instructions.textContent).toMatch(/lưu.*trước khi.*bộ nhiệm vụ mới/i);
  expect(instructions.textContent).toMatch(/thất bại.*chờ.*không.*mất/i);
});
