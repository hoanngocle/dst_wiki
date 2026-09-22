import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { PhamNhanConfigBrowser } from "./pham-nhan-config-browser";
import data from "@/app/data/pham-nhan-config.json";

it("shows all extracted options and their defaults including false", () => {
  const fixedEvaKeys = [
    "eva_health", "eva_hunger", "eva_sanity", "eva_hunger_rate", "eva_speed", "eva_dmg",
    "eva_life_key", "eva_wings_key", "eva_scythe_array_key", "eva_scythe_durability",
    "eva_scythe_dmg", "eva_scythe_recipe", "eva_hud", "eva_clothes",
  ];
  expect(data.options.every((option) => !fixedEvaKeys.includes(option.key))).toBe(true);
  expect(data.options).toHaveLength(3);

  render(<PhamNhanConfigBrowser />);
  expect(screen.getByRole("status").textContent).toBe(`${data.options.length} tùy chọn`);
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm config" }), { target: { value: "eva" } });
  expect(screen.getByRole("status").textContent).toBe("0 tùy chọn");
  expect(screen.getByText("Không tìm thấy config phù hợp.")).toBeDefined();
});

it("filters by group, supports accentless queries and empty results", () => {
  render(<PhamNhanConfigBrowser />);
  fireEvent.change(screen.getByLabelText("Nhóm config"), { target: { value: "Solo tích hợp" } });
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm config" }), { target: { value: "chi so" } });
  expect(screen.getByRole("heading", { name: "Solo: Chỉ Số" })).toBeDefined();
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm config" }), { target: { value: "not-a-config" } });
  expect(screen.getByText("Không tìm thấy config phù hợp.")).toBeDefined();
});
