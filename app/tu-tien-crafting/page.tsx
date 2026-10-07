import type { Metadata } from "next";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { TuTienCraftingBrowser } from "@/app/components/tu-tien-crafting-browser";
import { parseItemPayload } from "@/app/lib/item-catalog";
import { selectHanLapCraftables } from "@/app/lib/tu-tien-crafting";
import { buildDanLoCatalog } from "@/app/lib/tu-tien-danlo";
import catalogPayload from "@/public/data/catalog.json";
import itemsPayload from "@/public/data/items.json";

export const metadata: Metadata = {
  title: "Chế tạo Tu Tiên · Đan Lô | DST Wiki",
  description: "Tra cứu 78 công thức Đan Lô: đan dược, pháp bảo, trang bị và nguyên liệu; cùng đồ chế dành cho Hàn Lập.",
};
const allItems = parseItemPayload(itemsPayload);
const furnace = buildDanLoCatalog(allItems);
const furnaceIds = new Set(furnace.items.map(item => item.id));
const otherItems = selectHanLapCraftables(allItems, catalogPayload).items.filter(item => !furnaceIds.has(item.id));

export default function CraftingPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
    <SiteHeader active="tu-tien-crafting" />
    <DstPageShell><div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
      <DstHero testId="han-lap-crafting-hero" eyebrow={`Tu Tiên ${furnace.version} · Chế tạo`} title="Chế tạo Tu Tiên" description="Tra cứu nguyên liệu và thời gian luyện tại Đan Lô. Công thức được đối chiếu với Tu Tiên gốc ngày 07/10/2026." stats={[{ label: "Công thức Đan Lô", value: furnace.items.length + 1 }, { label: "Đồ chế khác của Hàn Lập", value: otherItems.length }]} statsAriaLabel="Tổng quan đồ chế Tu Tiên" />
      <TuTienCraftingBrowser furnaceItems={furnace.items} otherItems={otherItems} referenceItems={furnace.referenceItems} dynamicRecipe={furnace.dynamicRecipe} />
    </div></DstPageShell>
  </div>;
}
