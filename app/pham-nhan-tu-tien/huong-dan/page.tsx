import type { Metadata } from "next";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { PhamNhanNav } from "@/app/components/pham-nhan-nav";
import { PhamNhanGuides } from "@/app/components/pham-nhan-guides";

export const metadata: Metadata = { title: "Hướng dẫn | Phàm Nhân Tu Tiên", description: "Hướng dẫn các hệ thống đã tích hợp trong Phàm Nhân Tu Tiên." };

export default function PhamNhanGuidesPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text"><SiteHeader active="tu-tien-ky" /><DstPageShell><div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
    <DstHero eyebrow="Phàm Nhân Tu Tiên" title="Hướng dẫn" description="Công dụng, cách chơi, sản vật và bảng thưởng của các phần đã tích hợp." />
    <PhamNhanNav active="guides" /><PhamNhanGuides />
  </div></DstPageShell></div>;
}
