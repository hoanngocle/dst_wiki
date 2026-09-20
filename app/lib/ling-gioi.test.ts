import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { expect, it } from "vitest";
import { lingGioiItems, lingGioiSections } from "@/app/data/ling-gioi";
import source from "@/app/data/ling-gioi/source.json";
import manifest from "@/app/data/ling-gioi/source-manifest.json";
import { lingGioiImage } from "./ling-gioi";

it("covers every upstream entry and category with a complete Vietnamese translation", () => {
  expect(lingGioiSections).toHaveLength(source.sections.length);
  expect(lingGioiItems.map(item => item.id).sort()).toEqual(source.items.map(item => item.id).sort());
  expect(new Set(lingGioiItems.map(item => item.id)).size).toBe(source.items.length);
  for (const item of lingGioiItems) {
    expect(item.name).toBeTruthy();
    expect(item.summary).toBeTruthy();
    expect(item.details).toBeTruthy();
    expect(lingGioiSections.some(section => section.id === item.section)).toBe(true);
    const original = source.items.find(row => row.id === item.id)!;
    if (original["制作配方"]) expect(item.recipe).toBeTruthy();
    const prose = [item.name, item.summary, item.recipe, item.details, ...item.tags].join(" ").replace(/\[\[[^\]]+\]\]/g, "");
    expect(prose, item.id).not.toMatch(/[\u3400-\u9fff]/);
    const imagePaths = (text: string) => [...new Set(text.match(/images\/[\w./-]+\.(?:png|jpg|jpeg|gif|webp|svg)/g) || [])].sort();
    expect(imagePaths(item.recipe + item.details), item.id).toEqual(imagePaths(original["制作配方"] + original["详情"]));
  }
});

it("has a nonempty local copy of every referenced image", () => {
  for (const image of manifest.assets) {
    const path = join(process.cwd(), "public/ling-gioi", image.path);
    expect(existsSync(path), image.path).toBe(true);
    expect(readFileSync(path).length).toBe(image.bytes);
  }
  expect(lingGioiImage("images/../../secret.svg")).toBe("");
  expect(lingGioiImage("https://example.com/image.png")).toBe("");
});
