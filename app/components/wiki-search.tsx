"use client";

import { MagnifyingGlass, X } from "@phosphor-icons/react";
import { useEffect, useMemo, useRef, useState } from "react";

import { ItemResult } from "@/app/components/item-result";
import type { ItemFilter, ItemListEntry } from "@/app/lib/item-catalog";
import { filterItems, normalizeSearchText } from "@/app/lib/wiki-search";

const RESULT_BATCH_SIZE = 40;

const filters: readonly { value: ItemFilter; label: string }[] = [
  { value: "all", label: "Tất cả" },
  { value: "tu_tien", label: "Tu Tiên" },
  { value: "base_game", label: "DST gốc" },
  { value: "craftable", label: "Có công thức" },
];

export function WikiSearch({ items }: { items: readonly ItemListEntry[] }) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<ItemFilter>("all");
  const [visibleLimit, setVisibleLimit] = useState(RESULT_BATCH_SIZE);
  const inputRef = useRef<HTMLInputElement>(null);
  const results = useMemo(
    () => filterItems(items, query, filter),
    [filter, items, query],
  );
  const visibleResults = results.slice(0, visibleLimit);

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

  function updateQuery(nextQuery: string) {
    setQuery(nextQuery);
    setVisibleLimit(RESULT_BATCH_SIZE);
  }

  function updateFilter(nextFilter: ItemFilter) {
    setFilter(nextFilter);
    setVisibleLimit(RESULT_BATCH_SIZE);
  }

  function clearQueryAndFocus() {
    updateQuery("");
    inputRef.current?.focus();
  }

  function resetFilters() {
    setQuery("");
    setFilter("all");
    setVisibleLimit(RESULT_BATCH_SIZE);
    inputRef.current?.focus();
  }

  const countLabel = `${results.length} ${results.length === 1 ? "Item" : "Items"}`;
  const activeFilterLabel =
    filters.find((candidate) => candidate.value === filter)?.label ?? "Tất cả";
  const trimmedQuery = query.trim();
  const statusLabel = trimmedQuery
    ? `${countLabel} khớp với "${trimmedQuery}" trong ${activeFilterLabel}.`
    : `${countLabel} trong ${activeFilterLabel}.`;
  const resultsKey = JSON.stringify([
    filter,
    normalizeSearchText(query),
    results.map((item) => item.id),
  ]);

  return (
    <section aria-labelledby="item-results" className="mt-8">
      <div className="relative">
        <label
          htmlFor="item-search"
          className="mb-2 block text-sm font-medium text-[#263b58]"
        >
          Tìm kiếm Items.
        </label>
        <div className="relative">
          <MagnifyingGlass
            aria-hidden="true"
            size={20}
            weight="regular"
            className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#2e5fb3]"
          />
          <input
            ref={inputRef}
            id="item-search"
            type="search"
            value={query}
            onChange={(event) => updateQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Escape") updateQuery("");
            }}
            placeholder="Tìm theo tên, prefab hoặc nguyên liệu..."
            aria-describedby="item-search-help"
            className="h-14 w-full rounded-xl border border-[#a8b8cc] bg-[#f8fafc] pl-12 pr-28 text-base text-[#14233b] placeholder:text-[#53647a] shadow-[0_10px_28px_rgba(34,61,96,0.08)] outline-none transition focus:border-[#2e5fb3] focus:ring-4 focus:ring-[#2e5fb3]/15"
          />
          {query ? (
            <button
              type="button"
              onClick={clearQueryAndFocus}
              aria-label="Xóa tìm kiếm"
              className="absolute right-3 top-1/2 inline-flex min-h-11 -translate-y-1/2 items-center gap-1 rounded-lg px-2 py-1 text-sm text-[#53647a] transition hover:bg-[#e9eff6] active:scale-[0.98]"
            >
              <X aria-hidden="true" size={16} /> Xóa
            </button>
          ) : (
            <kbd className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 rounded-md border border-[#c7d1de] bg-[#eef3f8] px-2 py-1 font-mono text-xs text-[#53647a]">
              ⌘ K
            </kbd>
          )}
        </div>
        <p id="item-search-help" className="sr-only">
          Tìm theo tên tiếng Việt, tên tiếng Anh, prefab, mô tả hoặc nguyên liệu.
        </p>
      </div>

      <div
        role="group"
        className="mt-3 flex gap-2 overflow-x-auto pb-2"
        aria-label="Lọc Items"
      >
        {filters.map((candidate) => (
          <button
            key={candidate.value}
            type="button"
            aria-pressed={filter === candidate.value}
            onClick={() => updateFilter(candidate.value)}
            className="min-h-11 shrink-0 rounded-full border border-[#cbd5e1] px-3 py-1.5 text-sm font-medium text-[#5c6b80] transition hover:border-[#2e5fb3] hover:text-[#2e5fb3] active:scale-[0.98] aria-pressed:border-[#2e5fb3] aria-pressed:bg-[#2e5fb3] aria-pressed:text-[#f8fafc]"
          >
            {candidate.label}
          </button>
        ))}
      </div>

      <div className="mt-7 flex items-end justify-between gap-4">
        <h2
          id="item-results"
          className="text-lg font-semibold tracking-tight text-[#14233b]"
        >
          Danh sách Items
        </h2>
        <p aria-hidden="true" className="text-sm text-[#53647a]">
          {countLabel}
        </p>
        <p role="status" className="sr-only">
          {statusLabel}
        </p>
      </div>

      {results.length ? (
        <>
          <ul
            key={resultsKey}
            className="mt-4 grid grid-cols-1 gap-4 motion-safe:animate-[atlas-result-in_180ms_ease-out] md:grid-cols-2"
          >
            {visibleResults.map((item) => (
              <li key={item.id}>
                <ItemResult item={item} query={query} />
              </li>
            ))}
          </ul>
          {visibleResults.length < results.length ? (
            <div className="mt-7 flex justify-center">
              <button
                type="button"
                onClick={() =>
                  setVisibleLimit((current) =>
                    Math.min(current + RESULT_BATCH_SIZE, results.length),
                  )
                }
                className="min-h-11 rounded-xl border border-[#2e5fb3] px-5 py-2.5 text-sm font-semibold text-[#2e5fb3] transition hover:bg-[#e9eff6] active:scale-[0.98]"
              >
                Xem thêm
              </button>
            </div>
          ) : null}
        </>
      ) : (
        <div
          key={resultsKey}
          className="mt-4 rounded-2xl border border-[#cbd5e1] bg-[#f8fafc] px-6 py-14 text-center motion-safe:animate-[atlas-result-in_180ms_ease-out]"
        >
          <h3 className="text-lg font-semibold text-[#14233b]">
            Không tìm thấy Item
          </h3>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#53647a]">
            Thử từ khóa khác hoặc xóa bộ lọc hiện tại.
          </p>
          <button
            type="button"
            onClick={resetFilters}
            className="mt-5 min-h-11 rounded-xl bg-[#2e5fb3] px-4 py-2.5 text-sm font-semibold text-[#f8fafc] transition hover:bg-[#264f96] active:scale-[0.98]"
          >
            Xóa bộ lọc
          </button>
        </div>
      )}
    </section>
  );
}
