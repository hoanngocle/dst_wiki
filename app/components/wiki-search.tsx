"use client";

import { MagnifyingGlass, X } from "@phosphor-icons/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";

import { dstControlClassName, DstField } from "@/app/components/dst-field";
import { ItemDetailModal } from "@/app/components/item-detail-modal";
import { ItemResult } from "@/app/components/item-result";
import { DstPanel } from "@/app/components/dst-panel";
import { DstState } from "@/app/components/dst-state";
import type {
  ItemListEntry,
  ItemSourceFilter,
} from "@/app/lib/item-catalog";
import {
  countGameCategories,
  filterItems,
  GAME_CATEGORY_OPTIONS,
  type GameCategoryFilter,
  normalizeSearchText,
} from "@/app/lib/wiki-search";

const RESULT_BATCH_SIZE = 40;

const sourceFilters: readonly { value: ItemSourceFilter; label: string }[] = [
  { value: "all", label: "Tất cả" },
  { value: "base_game", label: "DST" },
  { value: "tu_tien", label: "Tu Tiên" },
];

function FilterGroup({ label, children }: { label: string; children: ReactNode }) {
  const visibleLabel = label.replace("Lọc theo ", "");

  return (
    <div role="group" aria-label={label} className="min-w-0">
      <p aria-hidden="true" className="mb-2 text-xs font-semibold text-nova-muted">
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
  ariaLabel,
}: {
  pressed: boolean;
  onClick: () => void;
  children: ReactNode;
  tone?: "accent" | "dark";
  ariaLabel?: string;
}) {
  const stateClasses = pressed
    ? tone === "dark"
      ? "border-nova-border-strong bg-nova-surface-raised text-nova-text"
      : "border-nova-accent bg-nova-surface-raised text-nova-accent"
    : "border-nova-border bg-nova-surface-soft text-nova-muted";

  return (
    <button
      type="button"
      aria-pressed={pressed}
      aria-label={ariaLabel}
      onClick={onClick}
      className={`min-h-11 shrink-0 cursor-pointer rounded-full border px-3 py-1.5 text-sm font-medium transition hover:border-nova-accent hover:text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent focus-visible:ring-offset-2 focus-visible:ring-offset-nova-surface active:scale-[0.98] motion-reduce:transform-none motion-reduce:transition-none ${stateClasses}`}
    >
      {children}
    </button>
  );
}

export function WikiSearch({ items }: { items: readonly ItemListEntry[] }) {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState<ItemSourceFilter>("all");
  const [category, setCategory] = useState<GameCategoryFilter>("all");
  const [visibleLimit, setVisibleLimit] = useState(RESULT_BATCH_SIZE);
  const [selectedItem, setSelectedItem] = useState<ItemListEntry | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const itemsById = useMemo(
    () => new Map(items.map((item) => [item.id, item] as const)),
    [items],
  );
  const sourceItems = useMemo(
    () => filterItems(items, "", source, "all", "all"),
    [items, source],
  );
  const categoryCounts = useMemo(
    () => countGameCategories(sourceItems),
    [sourceItems],
  );
  const visibleCategoryOptions = useMemo(
    () =>
      GAME_CATEGORY_OPTIONS.filter(
        (candidate) =>
          candidate.value === "all" || categoryCounts[candidate.value] > 0,
      ),
    [categoryCounts],
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
    setCategory("all");
    setVisibleLimit(RESULT_BATCH_SIZE);
  }

  function updateCategory(nextCategory: GameCategoryFilter) {
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
    GAME_CATEGORY_OPTIONS.find((candidate) => candidate.value === category)?.label ??
    "Tất cả";
  const trimmedQuery = query.trim();
  const statusLabel = trimmedQuery
    ? `${countLabel} khớp với "${trimmedQuery}" trong nguồn ${activeSourceLabel}, nhóm ${activeCategoryLabel}.`
    : `${countLabel} trong nguồn ${activeSourceLabel}, nhóm ${activeCategoryLabel}.`;
  const resultsKey = JSON.stringify([
    source,
    category,
    normalizeSearchText(query),
    results.map((item) => item.id),
  ]);

  return (
    <section aria-labelledby="item-results" className="mt-8">
      <DstField label="Tìm kiếm vật phẩm." htmlFor="item-search">
        <div className="relative">
          <MagnifyingGlass
            aria-hidden="true"
            size={20}
            weight="regular"
            className="pointer-events-none absolute top-1/2 left-4 -translate-y-1/2 text-nova-accent"
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
            placeholder="Tên Việt, tên Anh hoặc code..."
            aria-describedby="item-search-help"
            className={`${dstControlClassName} h-14 pr-28 pl-12 text-base shadow-[0_10px_28px_rgba(0,0,0,0.16)]`}
          />
          {query ? (
            <button
              type="button"
              onClick={clearQueryAndFocus}
              aria-label="Xóa tìm kiếm"
              className="absolute top-1/2 right-3 inline-flex min-h-11 -translate-y-1/2 cursor-pointer items-center gap-1 rounded-lg px-2 py-1 text-sm text-nova-muted transition hover:bg-nova-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent focus-visible:ring-offset-2 focus-visible:ring-offset-nova-surface-soft active:scale-[0.98] motion-reduce:transform-none motion-reduce:transition-none"
            >
              <X aria-hidden="true" size={16} /> Xóa
            </button>
          ) : (
            <kbd className="pointer-events-none absolute top-1/2 right-4 -translate-y-1/2 rounded-md border border-nova-border bg-nova-surface-raised px-2 py-1 font-mono text-xs text-nova-muted">
              ⌘ K
            </kbd>
          )}
        </div>
        <p id="item-search-help" className="sr-only">
          Tìm theo tên tiếng Việt, tên tiếng Anh, code prefab, Wiki, mô tả hoặc nguyên liệu.
        </p>
      </DstField>

      <DstPanel testId="dst-wiki-filter-panel" className="mt-5 grid gap-4 p-4">
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
          {visibleCategoryOptions.map((candidate) => (
            <FilterButton
              key={candidate.value}
              pressed={category === candidate.value}
              onClick={() => updateCategory(candidate.value)}
              tone="dark"
              ariaLabel={`${candidate.label}, ${categoryCounts[candidate.value]} vật phẩm`}
            >
              <span>{candidate.label}</span>
              <span
                aria-hidden="true"
                className="ml-1.5 rounded-full bg-current/10 px-1.5 py-0.5 font-mono text-[10px] tabular-nums"
              >
                {categoryCounts[candidate.value]}
              </span>
            </FilterButton>
          ))}
        </FilterGroup>
      </DstPanel>

      <div className="mt-7 flex items-end justify-between gap-4">
        <h2
          id="item-results"
          className="text-lg font-semibold tracking-tight text-nova-text"
        >
          Danh sách vật phẩm
        </h2>
        <p aria-hidden="true" className="text-sm text-nova-muted">
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
              <li
                key={item.id}
                className="[content-visibility:auto] [contain-intrinsic-size:auto_18rem]"
              >
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
                className="min-h-11 cursor-pointer rounded-xl border border-nova-accent px-5 py-2.5 text-sm font-semibold text-nova-accent transition hover:bg-nova-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent active:scale-[0.98] motion-reduce:transition-none"
              >
                Xem thêm
              </button>
            </div>
          ) : null}
        </>
      ) : (
        <div key={resultsKey} className="mt-4 motion-safe:animate-[atlas-result-in_180ms_ease-out]">
          <DstState
            tone="empty"
            title="Không tìm thấy vật phẩm"
            description="Thử từ khóa khác hoặc xóa bộ lọc hiện tại."
            actions={
              <button
                type="button"
                onClick={resetFilters}
                className="min-h-11 cursor-pointer rounded-xl border border-nova-accent bg-nova-surface-raised px-4 py-2.5 text-sm font-semibold text-nova-accent transition hover:border-nova-border-strong hover:text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent focus-visible:ring-offset-2 focus-visible:ring-offset-nova-surface active:scale-[0.98] motion-reduce:transform-none motion-reduce:transition-none"
              >
                Xóa bộ lọc
              </button>
            }
          />
        </div>
      )}
      {selectedItem ? (
        <ItemDetailModal
          item={selectedItem}
          itemsById={itemsById}
          onSelectItem={setSelectedItem}
          onClose={closeItemDetails}
        />
      ) : null}
    </section>
  );
}
