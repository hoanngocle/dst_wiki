import { SiteHeader } from "@/app/components/site-header";
import { WikiSearch } from "@/app/components/wiki-search";
import { parseItemPayload } from "@/app/lib/item-catalog";
import itemPayload from "@/public/data/items.json";

const items = parseItemPayload(itemPayload);

export default function Home() {
  return (
    <div className="min-h-[100dvh] bg-[#edf1f5] text-[#14233b]">
      <SiteHeader active="items" />
      <main>
        <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
          <div className="grid items-end gap-5 md:grid-cols-[minmax(0,1fr)_320px] md:gap-12">
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-[#2e5fb3]">
                Danh mục DST &amp; Tu Tiên
              </p>
              <h1 className="max-w-2xl text-4xl font-semibold leading-[1.04] tracking-[-0.04em] text-[#14233b] sm:text-5xl lg:text-6xl">
                Tra cứu Prefab
              </h1>
            </div>
            <p className="max-w-[38ch] text-base leading-7 text-[#53647a] md:justify-self-end">
              Tìm toàn bộ prefab DST và Tu Tiên theo tên, namespace, category hoặc
              nguyên liệu trong công thức.
            </p>
          </div>
          <WikiSearch items={items} />
        </div>
      </main>
    </div>
  );
}
