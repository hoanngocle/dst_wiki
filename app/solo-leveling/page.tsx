import type { Metadata } from "next";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { SoloLevelingBrowser } from "@/app/components/solo-leveling-browser";
import { visibleSoloLevelingGroups } from "@/app/lib/solo-leveling";
import data from "@/data/generated/solo-leveling.json";

export const metadata: Metadata = {
  title: "Solo Leveling | DST Wiki",
  description: "Wiki Solo Leveling đầy đủ: cách chơi, chế tạo, 60 nhiệm vụ ngày, hầm ngục, hiệp hội, thăng Rank, đệ tử và cường hoá.",
};

export default function SoloLevelingPage() {
  const pageData = { ...data, groups: visibleSoloLevelingGroups(data), files: [] };
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader active="solo-leveling" />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <DstHero eyebrow={`Saikuno · Phiên bản ${data.meta.version}`} title="Solo Leveling" description="Từ thợ săn Rank E đến Quân Vương Bóng Tối. Toàn bộ wiki, công thức, nhiệm vụ và hướng dẫn từ thư mục mod, tập hợp trong một nơi để tra cứu."
            stats={[{ label: "Nhiệm vụ ngày", value: 60 }, { label: "Nhiệm vụ Hiệp Hội", value: 60 }, { label: "Chủ đề", value: pageData.groups.length }, { label: "File trong mod", value: data.meta.files }]} statsAriaLabel="Tổng quan Solo Leveling" />
          <SoloLevelingBrowser data={pageData} />
        </div>
      </DstPageShell>
    </div>
  );
}
