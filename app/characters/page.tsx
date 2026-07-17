import { SiteHeader } from "@/app/components/site-header";
import { WikiSearch } from "@/app/components/wiki-search";
import { parseItemPayload } from "@/app/lib/item-catalog";
import itemPayload from "@/public/data/items.json";

const characters = parseItemPayload(itemPayload).filter(
  (item) => item.namespace === "tu_tien" && item.category === "character",
);

export default function CharactersPage() {
  return (
    <div className="min-h-[100dvh] bg-[#edf1f5] text-[#14233b]">
      <SiteHeader active="characters" />
      <main className="mx-auto max-w-7xl px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-[#2e5fb3]">
          Tu Tiên
        </p>
        <h1 className="text-4xl font-semibold tracking-[-0.04em] text-[#14233b] sm:text-5xl">
          Nhân vật
        </h1>
        <p className="mt-4 max-w-[64ch] text-base leading-7 text-[#53647a]">
          Hồ sơ, đặc điểm, năng lực và lời thoại của toàn bộ nhân vật chơi được.
        </p>
        <WikiSearch items={characters} />
      </main>
    </div>
  );
}
