import { expect, it } from "vitest";

import snapshot from "@/data/generated/nova-items.json";

const requiredPrefabs = [
  "xd_liandanlu",
  "ttk_boss_back_xh",
  "ttk_boss_zcyseed",
  "ttk_boss_core_baihu",
  "ttk_boss_core_jfsn",
  "ttk_boss_core_qlch",
  "ttk_boss_core_spiderqueen",
  "ttk_boss_core_stalke_fuben",
  "ttk_boss_core_deerclops_ziyun",
  "ttk_summon_baihu",
  "ttk_summon_jfsn",
  "ttk_summon_qlch",
  "ttk_summon_spiderqueen",
  "ttk_summon_stalke_fuben",
  "ttk_summon_deerclops_ziyun",
] as const;

it("identifies the current NOVA source and its dynamically registered inventory items", () => {
  expect(snapshot.meta.name).toBe("NOVA");
  expect(snapshot.meta.version).toBe("2.0.3");

  const prefabs = snapshot.items.map((item) => item.prefab);
  expect(new Set(prefabs).size).toBe(prefabs.length);
  expect(prefabs).not.toContain("eva_scythe");
  for (const prefab of requiredPrefabs) expect(prefabs).toContain(prefab);
});
