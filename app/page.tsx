import { SiteHeader } from "@/app/components/site-header";
import { WikiSearch } from "@/app/components/wiki-search";
import { wikiEntries } from "@/app/data/wiki-entries";

export default function Home() {
  return (
    <div className="min-h-[100dvh] bg-[#edf1f5] text-[#14233b]">
      <SiteHeader active="items" />
      <main>
        <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
          <div className="grid items-end gap-5 md:grid-cols-[minmax(0,1fr)_280px] md:gap-10">
            <h1 className="max-w-2xl text-4xl font-semibold leading-[1.02] tracking-[-0.045em] text-[#14233b] sm:text-5xl lg:text-6xl">
              Tìm nhanh.<br />Chơi tiếp.
            </h1>
            <p className="max-w-[34ch] text-base leading-7 text-[#53647a] md:justify-self-end">
              Tra cứu nhanh vật phẩm, sinh vật, nhiệm vụ và địa điểm.
            </p>
          </div>
          <WikiSearch entries={wikiEntries} />
        </div>
      </main>
    </div>
  );
}
