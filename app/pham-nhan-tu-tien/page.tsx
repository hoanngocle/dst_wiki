import type { Metadata } from "next";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { PhamNhanBrowser } from "@/app/components/pham-nhan-browser";
import { PhamNhanNav } from "@/app/components/pham-nhan-nav";
import { SiteHeader } from "@/app/components/site-header";
import type { PhamNhanSnapshot } from "@/app/lib/pham-nhan";
import data from "@/data/generated/pham-nhan-items.json";

export const metadata: Metadata = { title: "Phàm Nhân Tu Tiên | DST Wiki", description: "Item, công thức và hệ thống hiện hành của Phàm Nhân Tu Tiên." };

export default function PhamNhanTuTienPage() {
  const snapshot = data as PhamNhanSnapshot;
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text"><SiteHeader active="tu-tien-ky" /><DstPageShell><div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8"><DstHero eyebrow={`DST · ${snapshot.meta.name} ${snapshot.meta.version}`} title="Phàm Nhân Tu Tiên" description="Catalog được dựng từ source runtime hiện hành: công thức, nguồn nhận, Affix, hướng dẫn và cấu hình." stats={[{ label: "Vật phẩm", value: snapshot.items.length }, { label: "Công thức", value: snapshot.items.filter((item) => item.recipeStatus === "known").length }, { label: "Affix", value: snapshot.affixes.length }]} statsAriaLabel="Tổng quan Phàm Nhân" /><PhamNhanNav active="catalog" /><PhamNhanBrowser data={snapshot} /></div></DstPageShell></div>;
}
