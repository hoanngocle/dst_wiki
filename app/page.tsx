import { SiteHeader } from "@/app/components/site-header";
import { WikiSearch } from "@/app/components/wiki-search";
import { parseItemPayload } from "@/app/lib/item-catalog";
import { summarizeItems } from "@/app/lib/wiki-search";
import itemPayload from "@/public/data/items.json";

const items = parseItemPayload(itemPayload);
const summary = summarizeItems(items);

export default function Home() {
  return (
    <div className="min-h-[100dvh] bg-[#edf1f5] text-[#14233b]">
      <SiteHeader active="items" />
      <main>
        <div className="mx-auto max-w-7xl px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <div className="grid items-end gap-7 lg:grid-cols-[minmax(0,1fr)_minmax(420px,0.72fr)] lg:gap-12">
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-[#2e5fb3]">
                DST, Tu Tiên và Wiki
              </p>
              <h1 className="max-w-2xl text-4xl font-semibold leading-[1.04] tracking-[-0.04em] text-[#14233b] sm:text-5xl">
                Danh mục vật phẩm
              </h1>
              <p className="mt-4 max-w-[62ch] text-base leading-7 text-[#53647a]">
                Tra cứu vật phẩm, ảnh, công thức và nội dung Wiki đã lưu cục bộ.
              </p>
            </div>
            <dl
              aria-label="Tổng quan dữ liệu"
              className="grid grid-cols-3 overflow-hidden rounded-2xl border border-[#c7d2df] bg-[#f8fafc] shadow-[0_12px_30px_rgba(35,59,88,0.06)]"
            >
              {[
                ["Vật phẩm", summary.total],
                ["Bài Wiki", summary.wiki],
                ["Công thức", summary.recipes],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="border-r border-[#d7dfe8] px-3 py-4 last:border-r-0 sm:px-5"
                >
                  <dt className="text-xs font-medium text-[#607188]">{label}</dt>
                  <dd className="mt-1 text-xl font-semibold tracking-tight text-[#172943]">
                    {value}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
          <WikiSearch items={items} />
        </div>
      </main>
    </div>
  );
}
