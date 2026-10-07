import type { Metadata } from "next";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { PhamNhanBrowser } from "@/app/components/pham-nhan-browser";
import { PhamNhanNav } from "@/app/components/pham-nhan-nav";
import { SiteHeader } from "@/app/components/site-header";
import type { PhamNhanSnapshot } from "@/app/lib/pham-nhan";
import data from "@/data/generated/nova-items.json";

export const metadata: Metadata = { title: "NOVA | DST Wiki", description: "Vật phẩm, công thức và hệ thống hiện hành của NOVA." };

export default function NovaPage() {
  const snapshot = data as PhamNhanSnapshot;
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text"><SiteHeader active="nova" /><DstPageShell><div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8"><DstHero eyebrow={`DST · ${snapshot.meta.name} ${snapshot.meta.version}`} title="NOVA" description="Catalog được đối chiếu trực tiếp từ source runtime NOVA: prefab inventory, công thức, phần thưởng, Affix, hướng dẫn và cấu hình." stats={[{ label: "Vật phẩm", value: snapshot.items.length }, { label: "Công thức", value: snapshot.items.filter((item) => item.recipeStatus === "known").length }, { label: "Affix", value: snapshot.affixes.length }]} statsAriaLabel="Tổng quan NOVA" /><PhamNhanNav active="catalog" /><PhamNhanBrowser data={snapshot} /></div></DstPageShell></div>;
}
