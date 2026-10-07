import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import { parseItemPayload } from "@/app/lib/item-catalog";
import itemPayload from "@/public/data/items.json";

import CultivationGuidePage from "./page";

it("renders the strict cultivation guide with clickable catalog ingredients", () => {
  render(<CultivationGuidePage />);

  expect(
    screen.getByRole("heading", { level: 1, name: "Tu Tiên" }),
  ).toBeDefined();

  fireEvent.click(screen.getByRole("tab", { name: "Cảnh giới" }));
  const table = screen.getByRole("table", { name: "Thứ tự cảnh giới Tu Tiên" });
  expect(within(table).getAllByRole("row")).toHaveLength(16);
  expect(
    within(table).getByRole("row", {
      name: "Cảnh giới 15: Hóa Thần Hậu Kỳ → Phản Hư Sơ Kỳ",
    }),
  ).toBeDefined();
  expect(within(table).getAllByTestId("game-sprite").length).toBeGreaterThan(15);
  expect(screen.queryByText(/bổ sung Vòi Voi/i)).toBeNull();

  const doanTheRow = within(table).getByRole("row", {
    name: "Cảnh giới 2: Luyện Khí Trung Kỳ → Luyện Khí Hậu Kỳ",
  });
  const choiceGroup = within(doanTheRow).getByLabelText("Nguyên liệu bổ sung bắt buộc");
  expect(within(choiceGroup).getByRole("button", { name: "Vòi Voi Mùa Hè, số lượng 1" })).toBeDefined();
  expect(within(choiceGroup).getByRole("button", { name: "Vòi Voi Mùa Đông, số lượng 1" })).toBeDefined();
  expect(within(choiceGroup).getByText("hoặc")).toBeDefined();
  const vanTrungRow = within(table).getByRole("row", {
    name: "Cảnh giới 6: Trúc Cơ Hậu Kỳ → Kết Đan Sơ Kỳ",
  });
  const sporeGroup = within(vanTrungRow).getByLabelText("Nguyên liệu bổ sung bắt buộc");
  expect(within(sporeGroup).getByLabelText("Bào Tử Xanh Lục, số lượng 10")).toBeDefined();
  expect(within(sporeGroup).getByLabelText("Bào Tử Xanh Lam, số lượng 10")).toBeDefined();
  expect(within(sporeGroup).getByLabelText("Bào Tử Đỏ, số lượng 10")).toBeDefined();
  fireEvent.click(
    within(doanTheRow).getByRole("button", { name: "Pig Skin, số lượng 3" }),
  );

  expect(screen.getByRole("dialog", { name: "Pig Skin" })).toBeDefined();
});

it("opens crafting by default and navigates to mod content by tabs and hash", () => {
  window.history.replaceState(null, "", "/tu-tien");
  render(<CultivationGuidePage />);
  expect(screen.getByRole("heading", { level: 1, name: "Tu Tiên" })).toBeDefined();
  expect(screen.getByRole("tab", { name: "Chế tạo" }).getAttribute("aria-selected")).toBe("true");
  expect(screen.queryByRole("tab", { name: "Tiện Ích Client" })).toBeNull();
  expect(screen.queryByRole("tab", { name: "Tiện Ích Tu Tiên" })).toBeNull();
  expect(screen.queryByRole("group", { name: "Chọn nhóm chế tạo" })).toBeNull();
  const tuTienItems = parseItemPayload(itemPayload).filter(item => item.namespace === "tu_tien" && item.category !== "character");
  expect(screen.getByRole("status").textContent).toContain(`${tuTienItems.length} vật phẩm`);
  fireEvent.click(screen.getByRole("tab", { name: "Thần Khí" }));
  expect(window.location.hash).toBe("#than-khi");
  expect(screen.getByRole("heading", { name: "Thần Khí Tu Tiên" })).toBeDefined();
  expect(screen.getByRole("searchbox", { name: "Tìm trong Thần Khí Tu Tiên" })).toBeDefined();
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm trong Thần Khí Tu Tiên" }), { target: { value: "Linh Dược Sinh Mệnh" } });
  expect(screen.getByRole("heading", { name: "Linh Dược Sinh Mệnh" })).toBeDefined();
});
it("opens direct module links and switches tabs with the keyboard", () => {
  window.history.replaceState(null, "", "/tu-tien#ham-nguc");
  render(<CultivationGuidePage />);
  const dungeon = screen.getByRole("tab", { name: "Hầm Ngục" });
  expect(dungeon.getAttribute("aria-selected")).toBe("true");
  expect(screen.getByRole("heading", { name: "Hầm Ngục" })).toBeDefined();
  fireEvent.keyDown(dungeon, { key: "ArrowRight" });
  expect(screen.getByRole("tab", { name: "Chế tạo" }).getAttribute("aria-selected")).toBe("true");
  expect(document.activeElement).toBe(screen.getByRole("tab", { name: "Chế tạo" }));
  expect(window.location.hash).toBe("#che-tao");
  fireEvent.click(screen.getByRole("tab", { name: "Thành Tựu" }));
  expect(screen.getByRole("table", { name: "Bảng nhiệm vụ" })).toBeDefined();
  expect(screen.getByRole("table", { name: "Bảng Thành tựu" })).toBeDefined();
  expect(screen.getByRole("table", { name: "Bảng Perk" })).toBeDefined();
});
it("keeps the audited furnace recipe and ingredient details in the crafting tab", () => {
  window.history.replaceState(null, "", "/tu-tien");
  render(<CultivationGuidePage />);
  expect(screen.queryByRole("button", { name: "Đan Lô (78)" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Đồ chế khác của Hàn Lập (40)" })).toBeNull();
  expect(screen.queryByText("Vũ khí chuyên thuộc")).toBeNull();
  expect(screen.queryByRole("heading", { name: "Chế tạo Tu Tiên" })).toBeNull();
  expect(screen.queryByText(/Từ luyện đan, đột phá cảnh giới/)).toBeNull();
  expect(screen.queryByText(/Tra cứu chung các công thức/)).toBeNull();
  expect(screen.queryByText(/Chưa xác nhận vũ khí đầu ra/)).toBeNull();
  expect(screen.queryByRole("button", { name: /^Vũ Khí, / })).toBeNull();
  expect(screen.getByRole("button", { name: /^Đan Dược, / })).toBeDefined();
  fireEvent.change(screen.getByRole("searchbox"), { target: { value: "Thiên Nghịch Châu" } });
  fireEvent.click(screen.getByRole("button", { name: "Xem chi tiết Thiên Nghịch Châu" }));
  const modal = screen.getByRole("dialog", { name: "Thiên Nghịch Châu" });
  expect(within(modal).getByText(/Luyện tại Đan Lô/)).toBeDefined();
  expect(within(modal).getAllByText(/Tử Xá Ma Vũ/).length).toBeGreaterThan(0);
});

it("switches the current page when a header submenu link is selected", () => {
  window.history.replaceState(null, "", "/tu-tien");
  render(<CultivationGuidePage />);
  fireEvent.click(screen.getByRole("button", { name: "Mở các mục Tu Tiên" }));
  fireEvent.click(screen.getByRole("link", { name: "Thần Khí" }));
  expect(window.location.hash).toBe("#than-khi");
  expect(screen.getByRole("tab", { name: "Thần Khí" }).getAttribute("aria-selected")).toBe("true");
  expect(screen.getByRole("heading", { name: "Thần Khí Tu Tiên" })).toBeDefined();
});

it("shows local mod ingredient names even when they are outside the base catalog", () => {
  window.history.replaceState(null, "", "/tu-tien#than-khi");
  render(<CultivationGuidePage />);
  expect(screen.getByLabelText("Huyền Tinh Hạ Phẩm, số lượng 5")).toBeDefined();
});

it("renders source-backed equipment images and missing ingredient icons", () => {
  window.history.replaceState(null, "", "/tu-tien#than-khi");
  render(<CultivationGuidePage />);
  for (const name of ["Kim Kiếm", "Mộc Kiếm", "Hỏa Kiếm", "Thổ Kiếm", "Lôi Kiếm"]) {
    const icon = screen.getByRole("img", { name: `Ảnh ${name}` });
    expect(icon.getAttribute("data-missing")).toBeNull();
    expect(icon.getAttribute("style")).toContain("/assets/tu-tien-mods/");
  }
  const material = screen.getByLabelText("Huyền Tinh Hạ Phẩm, số lượng 5");
  expect(within(material).getByTestId("game-sprite").getAttribute("data-missing")).toBeNull();
});
