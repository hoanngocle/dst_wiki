import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";

import payload from "../../data/manual/achievement-level.json";
import { parseAchievementLevelData } from "@/app/lib/achievement-level";
import { AchievementLevelBrowser } from "./achievement-level-browser";

const data = parseAchievementLevelData(payload);

it("shows every task occurrence by default", () => {
  render(<AchievementLevelBrowser data={data} />);

  expect(screen.getByRole("status").textContent).toContain("763 nhiệm vụ");
  expect(screen.getAllByTestId("task-record")).toHaveLength(763);
  const blockHeadings = screen.getAllByTestId("task-block-heading");
  expect(blockHeadings.map((heading) => heading.textContent)).toEqual([
    "Nhiệm vụ nhân vật",
    "Nhiệm vụ theo mùa",
    "Nhiệm vụ lặp",
  ]);
  expect(screen.getAllByTestId("task-pool-heading")).toHaveLength(28);
});

it("filters tasks and resets to the full result set", () => {
  render(<AchievementLevelBrowser data={data} />);

  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm nhiệm vụ" }), {
    target: { value: "batilisk" },
  });
  expect(screen.getByRole("status").textContent).not.toContain("763 nhiệm vụ");
  expect(screen.getAllByTestId("task-record").length).toBeGreaterThan(1);

  fireEvent.click(screen.getByRole("button", { name: "Xóa bộ lọc nhiệm vụ" }));
  expect(screen.getByRole("status").textContent).toContain("763 nhiệm vụ");
});

it("filters repeat tasks by season", () => {
  render(<AchievementLevelBrowser data={data} />);

  fireEvent.change(screen.getByLabelText("Loại nhiệm vụ"), {
    target: { value: "repeat" },
  });
  fireEvent.change(screen.getByLabelText("Mùa"), {
    target: { value: "winter" },
  });

  expect(screen.getAllByTestId("task-record")).toHaveLength(18);
  expect(screen.getByRole("status").textContent).toContain("18 nhiệm vụ");
});

it("switches to achievements and filters a category", () => {
  render(<AchievementLevelBrowser data={data} />);

  fireEvent.mouseDown(screen.getByRole("tab", { name: "Thành tựu" }), {
    button: 0,
    ctrlKey: false,
  });
  expect(screen.getByRole("status").textContent).toContain("169 thành tựu");
  fireEvent.change(screen.getByLabelText("Danh mục thành tựu"), {
    target: { value: "Ăn uống" },
  });
  expect(screen.getAllByTestId("achievement-record")).toHaveLength(14);
});

it("switches to perks and exposes character rewards separately", () => {
  render(<AchievementLevelBrowser data={data} />);

  fireEvent.mouseDown(screen.getByRole("tab", { name: "Kỹ năng" }), {
    button: 0,
    ctrlKey: false,
  });
  expect(screen.getByRole("status").textContent).toContain("128 kỹ năng");
  expect(
    screen.getByRole("heading", { name: "Thưởng khi hoàn thành 2 nhiệm vụ" }),
  ).toBeDefined();
  expect(
    screen.getByRole("heading", { name: "Thưởng khi hoàn thành 4 nhiệm vụ" }),
  ).toBeDefined();
  const perkList = screen.getByRole("list", { name: "Danh sách kỹ năng" });
  expect(within(perkList).getAllByTestId("perk-record")).toHaveLength(128);
  expect(screen.getByRole("option", { name: "Wonkey" })).toBeDefined();

  fireEvent.change(screen.getByLabelText("Nhân vật của kỹ năng"), {
    target: { value: "Wonkey" },
  });
  expect(screen.getAllByTestId("perk-record")).toHaveLength(2);
});

it("renders source backticks as inline code", () => {
  render(<AchievementLevelBrowser data={data} />);

  const firstPrefab = screen.getAllByText("butterflymuffin")[0];
  expect(firstPrefab.tagName).toBe("CODE");
});

it("renders an empty state with a reset action", () => {
  render(<AchievementLevelBrowser data={data} />);

  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm nhiệm vụ" }), {
    target: { value: "không tồn tại 2937640068" },
  });
  expect(screen.getByText("Không có nhiệm vụ phù hợp")).toBeDefined();
  fireEvent.click(screen.getByRole("button", { name: "Xóa bộ lọc nhiệm vụ" }));
  expect(screen.getAllByTestId("task-record")).toHaveLength(763);
});
