import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { expect, it } from "vitest";
import snapshot from "@/data/generated/tu-tien-mod-sprites.json";
import mods from "@/data/generated/tu-tien-mods.json";

it("serves real, nonempty PNGs for every mapped mod icon", () => {
  for (const sprite of Object.values(snapshot.sprites)) {
    const path = resolve(process.cwd(), "public", sprite.src.slice(1));
    const png = readFileSync(path);
    expect(png.subarray(0, 8).toString("hex"), sprite.src).toBe("89504e470d0a1a0a");
    expect(png.readUInt32BE(16), sprite.src).toBeGreaterThan(0);
    expect(png.readUInt32BE(20), sprite.src).toBeGreaterThan(0);
  }
});

it("maps all permanent elixirs, affix stones and Nyx skill icons", () => {
  const sprites: Record<string, unknown> = snapshot.sprites;
  const categories = new Set(["Linh dược", "Đá thuộc tính", "Kỹ năng"]);
  const rows = mods.mods.flatMap(mod => mod.entries).filter(row => categories.has(row.category));
  expect(rows).toHaveLength(93);
  for (const row of rows) expect(sprites[row.id], row.title).toBeDefined();
});
