import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";

import CultivationGuidePage from "./page";

it("renders the strict cultivation guide with clickable catalog ingredients", () => {
  render(<CultivationGuidePage />);

  expect(
    screen.getByRole("heading", { level: 1, name: "Cảnh giới Tu Tiên" }),
  ).toBeDefined();
  expect(screen.getByRole("link", { name: "Cảnh giới Tu Tiên" }).getAttribute("aria-current")).toBe(
    "page",
  );
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
