import { render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";

vi.mock("@/app/components/achievement-level-browser", () => ({
  AchievementLevelBrowser: () => null,
}));

import AchievementLevelPage from "./page";

it("renders the complete Achievement & Level overview", () => {
  render(<AchievementLevelPage />);

  expect(
    screen.getByRole("link", { name: "Achievement & Level" }).getAttribute("aria-current"),
  ).toBe("page");
  expect(
    screen.getByRole("heading", { level: 1, name: "Achievement & Level" }),
  ).toBeDefined();
  const stats = screen.getByTestId("achievement-level-hero-stats");
  expect(within(stats).getByText("763")).toBeDefined();
  expect(within(stats).getByText("169")).toBeDefined();
  expect(within(stats).getByText("128")).toBeDefined();
  expect(within(stats).getByText("18")).toBeDefined();
  expect(screen.getByRole("heading", { name: "Hệ thống Level" })).toBeDefined();
  expect(screen.getByText(/Mặc định bắt đầu cấp 1/)).toBeDefined();
  expect(screen.getByRole("heading", { name: "Sao và mốc thưởng" })).toBeDefined();
  expect(screen.getByText(/Sao.*coinget/)).toBeDefined();
  expect(screen.getByText("Hồi 50 Máu, Đói và Sanity.")).toBeDefined();
  expect(screen.getByText("Nhận 1 Sao.")).toBeDefined();
});

it("renders player and pet level attributes from the artifact", () => {
  render(<AchievementLevelPage />);

  const playerTable = screen.getByRole("table", { name: "Thuộc tính người chơi" });
  const petTable = screen.getByRole("table", { name: "Thuộc tính pet" });

  expect(playerTable).toBeDefined();
  expect(petTable).toBeDefined();
  expect(playerTable.parentElement?.parentElement?.className).toContain("min-w-0");
  expect(petTable.parentElement?.parentElement?.className).toContain("min-w-0");
  expect(screen.getByText("Tốc độ pet")).toBeDefined();
});
