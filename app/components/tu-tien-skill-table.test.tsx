import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import { TuTienHub } from "./tu-tien-hub";
import mods from "@/data/generated/tu-tien-mods.json";
import sprites from "@/data/generated/tu-tien-mod-sprites.json";

it("shows every Nyx skill in a table with damage, effects and icons", () => {
  window.history.replaceState(null, "", "/tu-tien#nyx");
  render(<TuTienHub crafting={null} cultivation={null} mods={mods.mods} referenceItems={[]} sprites={sprites.sprites} />);
  const table=screen.getByRole("table", {name:"Kỹ năng Nyx"});
  expect(within(table).getAllByRole("row")).toHaveLength(10);
  expect(within(table).getAllByTestId("game-sprite")).toHaveLength(9);
  expect(within(table).getByText("67 × M₃₀ + W")).toBeDefined();
  expect(within(table).getByText(/20 × L \+ W/)).toBeDefined();
  expect(within(table).getAllByText("Không gây sát thương")).toHaveLength(3);
  expect(screen.queryByRole("option",{name:"Cảnh giới Nyx"})).toBeNull();
});

it("filters skill rows without pagination and preserves the other Nyx categories", () => {
  window.history.replaceState(null, "", "/tu-tien#nyx");
  render(<TuTienHub crafting={null} cultivation={null} mods={mods.mods} referenceItems={[]} sprites={sprites.sprites} />);
  fireEvent.change(screen.getByRole("combobox", {name:"Nhóm nội dung Nyx"}),{target:{value:"Kỹ năng"}});
  expect(screen.queryByRole("button",{name:"Sau"})).toBeNull();
  fireEvent.change(screen.getByRole("searchbox", {name:"Tìm trong Nyx"}),{target:{value:"Trảm Linh"}});
  expect(within(screen.getByRole("table",{name:"Kỹ năng Nyx"})).getAllByRole("row")).toHaveLength(2);
});
