import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { WikiSearch } from "@/app/components/wiki-search";
import { parseItemCatalog } from "@/app/lib/item-catalog";
import { summarizeItems } from "@/app/lib/wiki-search";
import itemPayload from "@/public/data/items.json";

const items = parseItemCatalog(itemPayload).filter(
  (item) => item.category !== "character",
);
const summary = summarizeItems(items);

export default function Home() {
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader active="items" />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <DstHero
            testId="item-catalog-hero"
            eyebrow="DST và Tu Tiên"
            title="Danh mục vật phẩm"
            description="Tra cứu vật phẩm, ảnh, công thức và nội dung Wiki đã lưu cục bộ."
            stats={[
              { label: "Vật phẩm", value: summary.total },
              { label: "Bài Wiki", value: summary.wiki },
              { label: "Công thức", value: summary.recipes },
            ]}
            statsAriaLabel="Tổng quan dữ liệu"
          />
          <WikiSearch items={items} />
        </div>
      </DstPageShell>
    </div>
  );
}
