"use client";

import { MagnifyingGlass, X } from "@phosphor-icons/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";

import { ItemDetailPeek } from "@/app/components/item-detail-peek";
import { ItemResult } from "@/app/components/item-result";
import type {
  ItemListEntry,
  ItemSourceFilter,
  PrefabCategoryFilter,
} from "@/app/lib/item-catalog";
import { filterItems, normalizeSearchText } from "@/app/lib/wiki-search";

const RESULT_BATCH_SIZE = 40;

const sourceFilters: readonly { value: ItemSourceFilter; label: string }[] = [
  { value: "all", label: "Tất cả" },
  { value: "base_game", label: "DST" },
  { value: "tu_tien", label: "Tu Tiên" },
];

const categoryFilters: readonly {
  value: PrefabCategoryFilter;
  label: string;
}[] = [
  { value: "all", label: "Tất cả loại" },
  { value: "item", label: "Item" },
  { value: "pill", label: "Đan Dược" },
  { value: "mob", label: "Mob" },
  { value: "boss", label: "Boss" },
  { value: "character", label: "Nhân vật" },
  { value: "structure", label: "Công trình" },
  { value: "effect", label: "Hiệu ứng" },
  { value: "other", label: "Khác" },
];

function FilterGroup({ label, children }: { label: string; children: ReactNode }) {
  const visibleLabel = label.replace("Lọc theo ", "");

  return (
    <div role="group" aria-label={label} className="min-w-0">
      <p aria-hidden="true" className="mb-2 text-xs font-semibold text-[#43556d]">
        {visibleLabel.charAt(0).toUpperCase() + visibleLabel.slice(1)}
      </p>
      <div className="flex gap-2 overflow-x-auto pb-1">{children}</div>
    </div>
  );
}

function FilterButton({
  pressed,
  onClick,
  children,
  tone = "accent",
}: {
  pressed: boolean;
  onClick: () => void;
  children: ReactNode;
  tone?: "accent" | "dark";
}) {
  const pressedClasses =
    tone === "dark"
      ? "aria-pressed:border-[#172943] aria-pressed:bg-[#172943]"
      : "aria-pressed:border-[#2e5fb3] aria-pressed:bg-[#2e5fb3]";

  return (
    <button
      type="button"
      aria-pressed={pressed}
      onClick={onClick}
      className={`min-h-11 shrink-0 cursor-pointer rounded-full border border-[#cbd5e1] px-3 py-1.5 text-sm font-medium text-[#5c6b80] transition hover:border-[#2e5fb3] hover:text-[#2e5fb3] active:scale-[0.98] aria-pressed:text-[#f8fafc] ${pressedClasses}`}
    >
      {children}
    </button>
  );
}

export function WikiSearch({ items }: { items: readonly ItemListEntry[] }) {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState<ItemSourceFilter>("all");
  const [category, setCategory] = useState<PrefabCategoryFilter>("all");
  const [visibleLimit, setVisibleLimit] = useState(RESULT_BATCH_SIZE);
  const [selectedItem, setSelectedItem] = useState<ItemListEntry | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const itemsById = useMemo(
    () => new Map(items.map((item) => [item.id, item] as const)),
    [items],
  );
  const results = useMemo(
    () => filterItems(items, query, source, category, "all"),
    [category, items, query, source],
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

  function updateSource(nextSource: ItemSourceFilter) {
    setSource(nextSource);
    setVisibleLimit(RESULT_BATCH_SIZE);
  }

  function updateCategory(nextCategory: PrefabCategoryFilter) {
    setCategory(nextCategory);
    setVisibleLimit(RESULT_BATCH_SIZE);
  }

  function clearQueryAndFocus() {
    updateQuery("");
    inputRef.current?.focus();
  }

  function resetFilters() {
    setQuery("");
    setSource("all");
    setCategory("all");
    setVisibleLimit(RESULT_BATCH_SIZE);
    inputRef.current?.focus();
  }

  const closeItemDetails = useCallback(() => setSelectedItem(null), []);

  const countLabel = `${results.length} vật phẩm`;
  const activeSourceLabel =
    sourceFilters.find((candidate) => candidate.value === source)?.label ?? "Tất cả";
  const activeCategoryLabel =
    categoryFilters.find((candidate) => candidate.value === category)?.label ??
    "Tất cả loại";
  const trimmedQuery = query.trim();
  const statusLabel = trimmedQuery
    ? `${countLabel} khớp với "${trimmedQuery}" trong ${activeSourceLabel}, ${activeCategoryLabel}.`
    : `${countLabel} trong ${activeSourceLabel}, ${activeCategoryLabel}.`;
  const resultsKey = JSON.stringify([
    source,
    category,
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
          Tìm kiếm vật phẩm.
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
            placeholder="Tìm theo tên, prefab, nội dung Wiki hoặc nguyên liệu..."
            aria-describedby="item-search-help"
            className="h-14 w-full rounded-xl border border-[#a8b8cc] bg-[#f8fafc] pl-12 pr-28 text-base text-[#14233b] placeholder:text-[#53647a] shadow-[0_10px_28px_rgba(34,61,96,0.08)] outline-none transition focus:border-[#2e5fb3] focus:ring-4 focus:ring-[#2e5fb3]/15"
          />
          {query ? (
            <button
              type="button"
              onClick={clearQueryAndFocus}
              aria-label="Xóa tìm kiếm"
              className="absolute right-3 top-1/2 inline-flex min-h-11 -translate-y-1/2 cursor-pointer items-center gap-1 rounded-lg px-2 py-1 text-sm text-[#53647a] transition hover:bg-[#e9eff6] active:scale-[0.98]"
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
          Tìm theo tên tiếng Việt, tên tiếng Anh, Wiki, prefab, mô tả hoặc nguyên liệu.
        </p>
      </div>

      <div className="mt-5 grid gap-4 rounded-2xl border border-[#c7d2df] bg-[#f8fafc] p-4 shadow-[0_10px_26px_rgba(34,61,96,0.05)]">
        <FilterGroup label="Lọc theo nguồn">
          {sourceFilters.map((candidate) => (
            <FilterButton
              key={candidate.value}
              pressed={source === candidate.value}
              onClick={() => updateSource(candidate.value)}
            >
              {candidate.label}
            </FilterButton>
          ))}
        </FilterGroup>
        <FilterGroup label="Lọc theo danh mục">
          {categoryFilters.map((candidate) => (
            <FilterButton
              key={candidate.value}
              pressed={category === candidate.value}
              onClick={() => updateCategory(candidate.value)}
              tone="dark"
            >
              {candidate.label}
            </FilterButton>
          ))}
        </FilterGroup>
      </div>

      <div className="mt-7 flex items-end justify-between gap-4">
        <h2
          id="item-results"
          className="text-lg font-semibold tracking-tight text-[#14233b]"
        >
          Danh sách vật phẩm
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
                <ItemResult
                  item={item}
                  query={query}
                  itemsById={itemsById}
                  onSelectItem={setSelectedItem}
                />
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
                className="min-h-11 cursor-pointer rounded-xl border border-[#2e5fb3] px-5 py-2.5 text-sm font-semibold text-[#2e5fb3] transition hover:bg-[#e9eff6] active:scale-[0.98]"
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
            Không tìm thấy vật phẩm
          </h3>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#53647a]">
            Thử từ khóa khác hoặc xóa bộ lọc hiện tại.
          </p>
          <button
            type="button"
            onClick={resetFilters}
            className="mt-5 min-h-11 cursor-pointer rounded-xl bg-[#2e5fb3] px-4 py-2.5 text-sm font-semibold text-[#f8fafc] transition hover:bg-[#264f96] active:scale-[0.98]"
          >
            Xóa bộ lọc
          </button>
        </div>
      )}
      {selectedItem ? (
        <ItemDetailPeek
          item={selectedItem}
          itemsById={itemsById}
          onSelectItem={setSelectedItem}
          onClose={closeItemDetails}
        />
      ) : null}
    </section>
  );
}
