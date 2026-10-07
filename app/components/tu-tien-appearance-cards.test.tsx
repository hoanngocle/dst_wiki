import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import { TuTienHub } from "./tu-tien-hub";
import mods from "@/data/generated/tu-tien-mods.json";
import sprites from "@/data/generated/tu-tien-mod-sprites.json";

it("shows all 36 Nyx appearance cards with distinct real build previews", () => {
  window.history.replaceState(null,"","/tu-tien#nyx");
  render(<TuTienHub crafting={null} cultivation={null} mods={mods.mods} referenceItems={[]} sprites={sprites.sprites} />);
  fireEvent.change(screen.getByRole("combobox",{name:"Nhóm nội dung Nyx"}),{target:{value:"Ngoại hình"}});
  const section=screen.getByRole("region",{name:"Ngoại hình Nyx"});
  expect(within(section).getAllByRole("article")).toHaveLength(36);
  expect(within(section).getAllByRole("img")).toHaveLength(36);
  const images=within(section).getAllByTestId("game-sprite");
  expect(images.every(image=>!image.hasAttribute("data-missing"))).toBe(true);
  expect(new Set(images.map(image=>image.style.backgroundImage)).size).toBe(36);
  expect(screen.queryByRole("button",{name:"Sau"})).toBeNull();
  fireEvent.change(screen.getByRole("searchbox",{name:"Tìm trong Nyx"}),{target:{value:"Vân Tiêu"}});
  expect(within(section).getAllByRole("article")).toHaveLength(3);
});
