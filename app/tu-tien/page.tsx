import type { Metadata } from "next";
import { CultivationBrowser } from "@/app/components/cultivation-browser";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { TuTienCraftingBrowser } from "@/app/components/tu-tien-crafting-browser";
import { TuTienHub, type ModWiki } from "@/app/components/tu-tien-hub";
import { buildCultivationStages } from "@/app/lib/cultivation-guide";
import { parseItemPayload } from "@/app/lib/item-catalog";
import { buildDanLoCatalog } from "@/app/lib/tu-tien-danlo";
import itemsPayload from "@/public/data/items.json";
import spriteSnapshot from "@/data/generated/tu-tien-mod-sprites.json";
import modSnapshot from "@/data/generated/tu-tien-mods.json";

export const metadata: Metadata = {
  title: "Tu Tiên | DST Wiki",
  description: "Chế tạo, cảnh giới và tra cứu các mod Nyx, Thành Tựu, Thần Khí, Công Trình và Hầm Ngục.",
};

const allItems = parseItemPayload(itemsPayload);
const furnace = buildDanLoCatalog(allItems);
const furnaceIds = new Set(furnace.items.map(item => item.id));
const otherItems = furnace.referenceItems.filter(
  item => item.namespace === "tu_tien" && item.category !== "character" && !furnaceIds.has(item.id),
);
const stages = buildCultivationStages(furnace.referenceItems);
const mods: ModWiki[] = modSnapshot.mods.filter(mod => mod.id !== "client" && mod.id !== "tien-ich" && mod.id !== "trang-phuc");

export default function TuTienPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
    <SiteHeader active="tu-tien" />
    <DstPageShell><div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
      <DstHero testId="tu-tien-hero" eyebrow={`Tu Tiên ${furnace.version} · Các mod mở rộng`} title="Tu Tiên" stats={[{ label: "Công thức Đan Lô", value: furnace.items.length + 1 }, { label: "Mod mở rộng", value: mods.length }]} statsAriaLabel="Tổng quan Tu Tiên" />
      <TuTienHub sprites={spriteSnapshot.sprites} mods={mods} referenceItems={furnace.referenceItems}
        crafting={<TuTienCraftingBrowser furnaceItems={furnace.items} otherItems={otherItems} referenceItems={furnace.referenceItems} />}
        cultivation={<section className="mt-8"><h2 className="text-2xl font-semibold">Cảnh giới Tu Tiên</h2><p className="mb-6 mt-2 text-nova-muted">15 bước thăng cấp và 5 mốc đột phá, cùng đan dược và nguyên liệu tương ứng.</p><CultivationBrowser stages={stages} referenceItems={furnace.referenceItems} /></section>} />
    </div></DstPageShell>
  </div>;
}
