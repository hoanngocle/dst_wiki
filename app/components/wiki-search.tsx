"use client";

import { MagnifyingGlass, X } from "@phosphor-icons/react";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  findNormalizedTextMatch,
  filterWikiEntries,
  normalizeSearchText,
  type SearchCategory,
  type WikiEntry,
} from "@/app/lib/wiki-search";

const categoryLabels: Record<WikiEntry["category"], string> = {
  item: "Vật phẩm",
  creature: "Sinh vật",
  location: "Địa điểm",
  quest: "Nhiệm vụ",
};

const filters: readonly { value: SearchCategory; label: string }[] = [
  { value: "all", label: "Tất cả" },
  { value: "item", label: categoryLabels.item },
  { value: "creature", label: categoryLabels.creature },
  { value: "location", label: categoryLabels.location },
  { value: "quest", label: categoryLabels.quest },
];

const accentClasses: Record<WikiEntry["accent"], string> = {
  ice: "bg-[#d6e2ef] text-[#315d91]",
  moss: "bg-[#dce5da] text-[#436247]",
  sand: "bg-[#e8dfd1] text-[#795f3d]",
  slate: "bg-[#d9dee6] text-[#46566d]",
};

function HighlightedText({ text, query }: { text: string; query: string }) {
  const match = findNormalizedTextMatch(text, query);
  if (!match) return text;

  return (
    <>
      <span className="sr-only">{text}</span>
      <span aria-hidden="true">
        {text.slice(0, match.start)}
        <mark className="rounded-sm bg-[#dce7f7] px-0.5 text-inherit">
          {text.slice(match.start, match.end)}
        </mark>
        {text.slice(match.end)}
      </span>
    </>
  );
}

export function WikiSearch({ entries }: { entries: readonly WikiEntry[] }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<SearchCategory>("all");
  const inputRef = useRef<HTMLInputElement>(null);
  const results = useMemo(
    () => filterWikiEntries(entries, query, category),
    [entries, query, category],
  );

  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      const isEditable =
        target?.isContentEditable ||
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.tagName === "SELECT";

      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        inputRef.current?.focus();
      } else if (event.key === "/" && !isEditable) {
        event.preventDefault();
        inputRef.current?.focus();
      }
    }

    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, []);

  function clearQueryAndFocus() {
    setQuery("");
    inputRef.current?.focus();
  }

  function resetFilters() {
    setQuery("");
    setCategory("all");
    inputRef.current?.focus();
  }

  const countLabel = `${results.length} mục`;
  const activeFilterLabel =
    filters.find((filter) => filter.value === category)?.label ?? "Tất cả";
  const trimmedQuery = query.trim();
  const statusLabel = trimmedQuery
    ? `${countLabel} khớp với "${trimmedQuery}" trong ${activeFilterLabel}.`
    : `${countLabel} trong ${activeFilterLabel}.`;
  const resultsKey = JSON.stringify([
    category,
    normalizeSearchText(query),
    results.map((entry) => entry.id),
  ]);

  return (
    <section aria-labelledby="atlas-results" className="mt-8">
      <div className="relative">
        <label htmlFor="atlas-search" className="mb-2 block text-sm font-medium text-[#263b58]">
          Tìm kiếm Items.
        </label>
        <div className="relative">
          <MagnifyingGlass aria-hidden="true" size={20} weight="regular" className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#2e5fb3]" />
          <input
            ref={inputRef}
            id="atlas-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Escape") setQuery("");
            }}
            placeholder="Tìm vật phẩm, sinh vật, địa điểm..."
            aria-describedby="atlas-search-help"
            className="h-14 w-full rounded-[10px] border border-[#a8b8cc] bg-[#f8fafc] pl-12 pr-28 text-base text-[#14233b] placeholder:text-[#53647a] shadow-[0_10px_28px_rgba(34,61,96,0.08)] outline-none transition focus:border-[#2e5fb3] focus:ring-4 focus:ring-[#2e5fb3]/15"
          />
          {query ? (
            <button type="button" onClick={clearQueryAndFocus} aria-label="Xoá tìm kiếm" className="absolute right-3 top-1/2 inline-flex min-h-11 -translate-y-1/2 items-center gap-1 rounded-md px-2 py-1 text-sm text-[#53647a] hover:bg-[#e9eff6] active:scale-[0.98]">
              <X aria-hidden="true" size={16} /> Xoá
            </button>
          ) : (
            <kbd className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 rounded-md border border-[#c7d1de] bg-[#eef3f8] px-2 py-1 font-mono text-xs text-[#53647a]">⌘ K</kbd>
          )}
        </div>
        <p id="atlas-search-help" className="sr-only">Tìm theo tên, mô tả, danh mục hoặc từ khoá.</p>
      </div>

      <div role="group" className="mt-3 flex gap-2 overflow-x-auto pb-2" aria-label="Lọc mục theo danh mục">
        {filters.map((filter) => (
          <button key={filter.value} type="button" aria-pressed={category === filter.value} onClick={() => setCategory(filter.value)} className="min-h-11 shrink-0 rounded-full border border-[#cbd5e1] px-3 py-1.5 text-sm font-medium text-[#5c6b80] transition hover:border-[#2e5fb3] hover:text-[#2e5fb3] active:scale-[0.98] aria-pressed:border-[#2e5fb3] aria-pressed:bg-[#2e5fb3] aria-pressed:text-[#f8fafc]">
            {filter.label}
          </button>
        ))}
      </div>

      <div className="mt-7 flex items-end justify-between gap-4">
        <h2 id="atlas-results" className="text-lg font-semibold tracking-tight text-[#14233b]">Khám phá Items</h2>
        <p aria-hidden="true" className="text-sm text-[#53647a]">
          {countLabel}
        </p>
        <p role="status" className="sr-only">
          {statusLabel}
        </p>
      </div>

      {results.length ? (
        <ul
          key={resultsKey}
          className="mt-3 border-t border-[#cbd5e1] motion-safe:animate-[atlas-result-in_180ms_ease-out]"
        >
          {results.map((entry) => (
            <li key={entry.id} className="grid grid-cols-[48px_minmax(0,1fr)_auto] items-center gap-3 border-b border-[#cbd5e1] py-4 md:grid-cols-[48px_minmax(0,1fr)_auto] md:gap-4">
              <div aria-hidden="true" className={`flex h-11 w-12 items-center justify-center rounded-md font-mono text-xs font-semibold uppercase ${accentClasses[entry.accent]}`}>{categoryLabels[entry.category].split(" ").map((word) => word[0]).join("")}</div>
              <div className="min-w-0">
                <h3 className="font-semibold text-[#172943]"><HighlightedText text={entry.name} query={query} /></h3>
                <p className="mt-1 line-clamp-2 text-sm leading-6 text-[#53647a]"><HighlightedText text={entry.description} query={query} /></p>
              </div>
              <span className="inline-flex rounded-full bg-[#dce6f4] px-2.5 py-1 text-xs font-medium text-[#2e5fb3]">{categoryLabels[entry.category]}</span>
            </li>
          ))}
        </ul>
      ) : (
        <div
          key={resultsKey}
          className="mt-3 border-y border-[#cbd5e1] py-14 text-center motion-safe:animate-[atlas-result-in_180ms_ease-out]"
        >
          <h3 className="text-lg font-semibold text-[#14233b]">Không tìm thấy mục nào</h3>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#53647a]">Hãy thử từ khoá khác hoặc xoá bộ lọc hiện tại.</p>
          <button type="button" onClick={resetFilters} className="mt-5 min-h-11 rounded-[10px] bg-[#2e5fb3] px-4 py-2.5 text-sm font-semibold text-[#f8fafc] transition hover:bg-[#264f96] active:scale-[0.98]">Xoá bộ lọc</button>
        </div>
      )}
    </section>
  );
}
