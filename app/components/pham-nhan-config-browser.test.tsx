import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import { PhamNhanConfigBrowser } from "./pham-nhan-config-browser";
import data from "@/app/data/pham-nhan-config.json";

it("shows all extracted options and their defaults including false", () => {
  render(<PhamNhanConfigBrowser />);
  expect(screen.getByRole("status").textContent).toBe(`${data.options.length} tùy chọn`);
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm config" }), { target: { value: "eva_clothes" } });
  expect(screen.getByRole("status").textContent).toBe("1 tùy chọn");
  const card = screen.getByRole("heading", { name: "EVA: Ẩn hình trang bị" }).closest("article")!;
  expect(within(card).getByText(/Mặc định:/).parentElement?.textContent).toContain("Tắt");
});

it("filters by group, supports accentless queries and empty results", () => {
  render(<PhamNhanConfigBrowser />);
  fireEvent.change(screen.getByLabelText("Nhóm config"), { target: { value: "EVA" } });
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm config" }), { target: { value: "hon luc" } });
  expect(screen.getByRole("heading", { name: "EVA: Khung hiển thị Hồn Lực" })).toBeDefined();
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm config" }), { target: { value: "not-a-config" } });
  expect(screen.getByText("Không tìm thấy config phù hợp.")).toBeDefined();
});
