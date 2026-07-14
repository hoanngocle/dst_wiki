import { WikiSearch } from "@/app/components/wiki-search";
import { wikiEntries } from "@/app/data/wiki-entries";

export default function Home() {
  return (
    <main className="min-h-[100dvh] bg-[#edf1f5] text-[#14233b]">
      <header className="border-b border-[#cbd5e1] bg-[#f8fafc]/90">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3 font-semibold tracking-[0.08em]">
            <span aria-hidden="true" className="h-4 w-4 rotate-45 border-2 border-[#2e5fb3]" />
            <span>FROST ATLAS</span>
          </div>
          <span className="hidden font-mono text-xs text-[#53647a] sm:block">{wikiEntries.length} entries</span>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
        <div className="grid items-end gap-5 md:grid-cols-[minmax(0,1fr)_280px] md:gap-10">
          <h1 className="max-w-2xl text-4xl font-semibold leading-[1.02] tracking-[-0.045em] text-[#14233b] sm:text-5xl lg:text-6xl">
            Find answers.<br />Keep playing.
          </h1>
          <p className="max-w-[34ch] text-base leading-7 text-[#53647a] md:justify-self-end">
            A fast reference for items, creatures, quests and locations.
          </p>
        </div>
        <WikiSearch entries={wikiEntries} />
      </div>
    </main>
  );
}
