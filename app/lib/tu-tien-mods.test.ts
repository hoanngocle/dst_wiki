import { expect, it } from "vitest";
import snapshot from "@/data/generated/tu-tien-mods.json";

it("publishes the eight local mods without mixing in Solo Leveling", () => {
  expect(snapshot.mods.map(mod => mod.id)).toEqual(["nyx", "thanh-tuu", "than-khi", "cong-trinh", "ham-nguc", "trang-phuc", "tien-ich", "client"]);
  for (const mod of snapshot.mods) {
    expect(new Set(mod.entries.map(row => row.id)).size).toBe(mod.entries.length);
    expect(mod.entries.length).toBeGreaterThan(0);
    expect(mod.sources.every(source => /^[a-f0-9]{64}$/.test(source.sha256))).toBe(true);
  }
});

it("keeps exact material quantities and permanent elixir limits from Than Khi", () => {
  const mod = snapshot.mods.find(mod => mod.id === "than-khi")!;
  expect(mod.entries.filter(row => row.category === "Đá thuộc tính")).toHaveLength(78);
  expect(mod.entries.filter(row => row.category === "Linh dược")).toHaveLength(6);
  const elixir = mod.entries.find(row => row.id === "tbc_elixir_health")!;
  expect(elixir.ingredients).toEqual([{ prefab: "royal_jelly", amount: 2 }, { prefab: "yellowgem", amount: 2 }, { prefab: "xd_lingshi3", amount: 5 }]);
  expect(elixir.facts).toContainEqual({ label: "Tối đa", value: "10 lần" });
  const top = mod.entries.find(row => row.id === "strengthen:16")!;
  expect(top.facts).toContainEqual({ label: "Sát thương chuẩn", value: "500" });
});

it("retains seasonal quests and Nyx's rare crafting recipes", () => {
  const achievements = snapshot.mods.find(mod => mod.id === "thanh-tuu")!;
  expect(achievements.entries.filter(row => row.category === "Nhiệm vụ mùa")).toHaveLength(192);
  const nyx = snapshot.mods.find(mod => mod.id === "nyx")!;
  expect(nyx.entries.filter(row => row.category === "Ngoại hình")).toHaveLength(36);
  expect(nyx.entries.find(row => row.id === "recipe:nyx_xd_htz_qzj")!.ingredients).toContainEqual({ prefab: "ttk_huyen_tinh_thuong_pham", amount: 5 });
});
