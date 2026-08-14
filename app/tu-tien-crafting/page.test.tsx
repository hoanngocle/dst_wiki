import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";

import HanLapCraftingPage from "./page";

it("renders only verified Hàn Lập craftables with full catalog references", () => {
  render(<HanLapCraftingPage />);

  expect(
    screen.getByRole("heading", { level: 1, name: "Đồ chế Tu Tiên của Hàn Lập" }),
  ).toBeDefined();
  expect(screen.getByRole("link", { name: "Chế tạo Tu Tiên" }).getAttribute("aria-current")).toBe(
    "page",
  );
  expect(screen.getByText("Đoán Thể Hoàn")).toBeDefined();
  expect(screen.queryByText("Cẩm Môn")).toBeNull();
  expect(screen.queryByRole("group", { name: "Lọc theo nguồn" })).toBeNull();
  expect(screen.getByRole("group", { name: "Lọc theo danh mục" })).toBeDefined();

  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), {
    target: { value: "Đoán Thể Hoàn" },
  });

  const result = screen
    .getByRole("button", { name: "Xem chi tiết Đoán Thể Hoàn" })
    .closest("li") as HTMLElement;
  fireEvent.click(within(result).getByRole("button", { name: "Pig Skin, số lượng 3" }));

  expect(screen.getByRole("dialog", { name: "Pig Skin" })).toBeDefined();
});
