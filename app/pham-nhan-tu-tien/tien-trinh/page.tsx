import type { Metadata } from "next";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { PhamNhanNav } from "@/app/components/pham-nhan-nav";
import { PhamNhanProgression } from "@/app/components/pham-nhan-progression";
import data from "@/data/generated/pham-nhan-progression.json";

export const metadata: Metadata = {
  title: "Tiến trình | Phàm Nhân Tu Tiên",
  description: "Thành tựu, Star, kỹ năng, nhiệm vụ mùa, đan dược và hạng nhân vật trong Phàm Nhân Tu Tiên.",
};

export default function PhamNhanProgressionPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text"><SiteHeader active="tu-tien-ky" /><DstPageShell><div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
    <DstHero eyebrow="Phàm Nhân Tu Tiên 2.0" title="Tiến trình Phàm Nhân Tu Tiên" description="Tra cứu thành tựu, kỹ năng Star, nhiệm vụ mùa và con đường tu luyện." stats={[
      { label: "Thành tựu", value: data.achievements.length },
      { label: "Nhóm", value: data.groups.length },
      { label: "Star thành tựu", value: data.achievements.reduce((total, row) => total + row.reward, 0) },
      { label: "Kỹ năng trong danh mục", value: data.perks.length },
      { label: "Star toàn bộ danh mục", value: data.perks.reduce((total, row) => total + row.maxCost, 0) },
    ]} statsAriaLabel="Tổng quan tiến trình" />
    <PhamNhanNav active="progression" /><PhamNhanProgression />
  </div></DstPageShell></div>;
}
