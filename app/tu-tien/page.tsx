import type { Metadata } from "next";

import { CultivationBrowser } from "@/app/components/cultivation-browser";
import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { buildCultivationStages } from "@/app/lib/cultivation-guide";
import { parseItemCatalog } from "@/app/lib/item-catalog";
import itemPayload from "@/public/data/items.json";

export const metadata: Metadata = {
  title: "Cảnh giới Tu Tiên | DST Wiki",
  description: "Lộ trình 15 lần thăng cấp Tu Tiên cùng đan dược và nguyên liệu tương ứng.",
};

const items = parseItemCatalog(itemPayload);
const stages = buildCultivationStages(items);

export default function CultivationGuidePage() {
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader active="tu-tien" />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <DstHero
            testId="cultivation-hero"
            eyebrow="Tu Tiên · Thứ tự tu luyện"
            title="Cảnh giới Tu Tiên"
            description="Lộ trình 15 lần thăng cấp, từ cảnh giới hiện tại qua đan dược tương ứng đến cảnh giới đạt được."
            stats={[
              { label: "Bước thăng cấp", value: stages.length },
              {
                label: "Mốc đột phá",
                value: stages.filter((stage) => stage.breakthrough).length,
              },
            ]}
            statsAriaLabel="Tổng quan lộ trình Tu Tiên"
          />
          <div className="mt-8">
            <CultivationBrowser stages={stages} referenceItems={items} />
          </div>
        </div>
      </DstPageShell>
    </div>
  );
}
