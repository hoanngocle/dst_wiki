import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import { TuTienHub } from "./tu-tien-hub";
import mods from "@/data/generated/tu-tien-mods.json";
import sprites from "@/data/generated/tu-tien-mod-sprites.json";

it("opens dungeon tables with accurate reward chances and item icons", () => {
  window.history.replaceState(null, "", "/tu-tien#ham-nguc");
  render(<TuTienHub crafting={null} cultivation={null} mods={mods.mods} referenceItems={[]} sprites={sprites.sprites} />);
  const rewards = screen.getByRole("table", { name: "Phần thưởng Hầm Ngục" });
  expect(within(rewards).getAllByRole("row")).toHaveLength(7);
  expect(within(rewards).getAllByTestId("game-sprite")).toHaveLength(8);
  expect(within(rewards).getAllByText("50%")).toHaveLength(2);
  expect(within(rewards).getAllByText("100%")).toHaveLength(4);
  expect(within(screen.getByRole("table", { name: "Boss Hầm Ngục" })).getAllByRole("row")).toHaveLength(7);
  expect(screen.getByText(/960 giây/)).toBeDefined();
  expect(screen.getByText(/180 giây/)).toBeDefined();
  expect(screen.queryByRole("button", { name: "Sau" })).toBeNull();
});

it("searches dungeon rewards by prefab and keeps source icons for gate and recovery bag", () => {
  window.history.replaceState(null, "", "/tu-tien#ham-nguc");
  render(<TuTienHub crafting={null} cultivation={null} mods={mods.mods} referenceItems={[]} sprites={sprites.sprites} />);
  const objects = screen.getByRole("table", { name: "Đồ dùng Hầm Ngục" });
  expect(within(objects).getAllByTestId("game-sprite")).toHaveLength(4);
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm trong Hầm Ngục" }), { target: { value: "ttk_huyen_tinh_trung_pham" } });
  expect(within(screen.getByRole("table", { name: "Phần thưởng Hầm Ngục" })).getAllByRole("row")).toHaveLength(2);
});
