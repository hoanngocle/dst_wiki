import type { Metadata } from "next";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { PhamNhanNav } from "@/app/components/pham-nhan-nav";
import { PhamNhanConfigBrowser } from "@/app/components/pham-nhan-config-browser";
import data from "@/app/data/pham-nhan-config.json";

export const metadata: Metadata = { title: "Config | Phàm Nhân Tu Tiên", description: "Tra cứu các tùy chọn, giá trị mặc định và cấu hình của mod Phàm Nhân Tu Tiên." };

export default function PhamNhanConfigPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text"><SiteHeader active="tu-tien-ky" /><DstPageShell><div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
    <DstHero eyebrow={`Phàm Nhân Tu Tiên ${data.version}`} title="Config" description="Tùy chọn của mod, giá trị mặc định và những lựa chọn có sẵn." stats={[{ label: "Tùy chọn", value: data.options.length }, { label: "Nhóm", value: new Set(data.options.map((option) => option.group)).size }]} statsAriaLabel="Tổng quan cấu hình" />
    <PhamNhanNav active="config" /><PhamNhanConfigBrowser />
  </div></DstPageShell></div>;
}
