import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import snapshot from "@/data/generated/tu-tien-mods.json";
import { TuTienAchievements } from "./tu-tien-achievements";
const mod = snapshot.mods.find(mod => mod.id === "thanh-tuu")!;

it("lists quests, achievements and perks in tables without configs", () => {
  render(<TuTienAchievements mod={mod} />);
  expect(within(screen.getByRole("table", { name: "Bảng nhiệm vụ" })).getAllByRole("row")).toHaveLength(193);
  expect(within(screen.getByRole("table", { name: "Bảng Thành tựu" })).getAllByRole("row")).toHaveLength(318);
  const perks = screen.getByRole("table", { name: "Bảng Perk" });
  expect(within(perks).getAllByRole("row")).toHaveLength(71);
  expect(within(perks).getByRole("row", { name: /Kích thước.*10/ })).toBeDefined();
  expect(screen.queryByText("Hoàn điểm khi đặt lại")).toBeNull();
  expect(screen.queryByText("Cấu hình")).toBeNull();
});

it("searches each table and filters quests by season", () => {
  render(<TuTienAchievements mod={mod} />);
  fireEvent.change(screen.getByRole("combobox", { name: "Mùa nhiệm vụ" }), { target: { value: "Xuân" } });
  expect(within(screen.getByRole("table", { name: "Bảng nhiệm vụ" })).getAllByRole("row")).toHaveLength(49);
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm Perk" }), { target: { value: "phong thu" } });
  const perks = screen.getByRole("table", { name: "Bảng Perk" });
  expect(within(perks).getAllByRole("row")).toHaveLength(3);
  expect(within(perks).getByText("Phòng thủ +")).toBeDefined();
  expect(screen.getByText(/4 rương thưởng/)).toBeDefined();
});
