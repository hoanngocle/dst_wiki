import { WikiSearch } from "@/app/components/wiki-search";
import { parseItemPayload } from "@/app/lib/item-catalog";
import itemPayload from "@/public/data/items.json";

const items = parseItemPayload(itemPayload);

export default function Home() {
  return (
    <main className="min-h-[100dvh] bg-[#edf1f5] text-[#14233b]">
      <header className="border-b border-[#cbd5e1] bg-[#f8fafc]/95">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <span
              aria-hidden="true"
              className="grid h-8 w-8 place-items-center rounded-lg border border-[#a8b8cc] bg-[#edf3fb]"
            >
              <span className="h-3.5 w-3.5 rotate-45 border-2 border-[#2e5fb3]" />
            </span>
            <div className="leading-tight">
              <p className="text-sm font-semibold tracking-[0.04em] text-[#172943]">
                Don&apos;t Starve Together
              </p>
              <p className="text-[11px] text-[#607188]">Wiki vật phẩm Tu Tiên</p>
            </div>
          </div>
          <span className="hidden font-mono text-xs text-[#53647a] md:block">
            {items.length} Items
          </span>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
        <div className="grid items-end gap-5 md:grid-cols-[minmax(0,1fr)_320px] md:gap-12">
          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-[#2e5fb3]">
              Danh mục chế tạo
            </p>
            <h1 className="max-w-2xl text-4xl font-semibold leading-[1.04] tracking-[-0.04em] text-[#14233b] sm:text-5xl lg:text-6xl">
              Tra cứu vật phẩm
            </h1>
          </div>
          <p className="max-w-[38ch] text-base leading-7 text-[#53647a] md:justify-self-end">
            Tìm nhanh tên, prefab và công thức của vật phẩm Tu Tiên cùng các nguyên
            liệu DST gốc liên quan.
          </p>
        </div>
        <WikiSearch items={items} />
      </div>
    </main>
  );
}
