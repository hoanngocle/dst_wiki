import { X } from "@phosphor-icons/react";
import { useEffect, useId, useRef } from "react";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { hasRealPrefab } from "@/app/lib/wiki-search";
import { GameSprite } from "./game-sprite";
import { RecipeIngredients } from "./recipe-ingredients";
import { WikiArticle } from "./wiki-article";

const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(",");

const categoryLabel = {
  item: "Item",
  mob: "Mob",
  boss: "Boss",
  character: "Nhân vật",
  structure: "Công trình",
  effect: "Hiệu ứng",
  other: "Khác",
} as const;

export function ItemDetailModal({
  item,
  onClose,
}: {
  item: ItemListEntry;
  onClose: () => void;
}) {
  const titleId = useId();
  const dialogRef = useRef<HTMLElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const sourceLabel = item.wiki
    ? "Wiki"
    : item.namespace === "tu_tien"
      ? "Tu Tiên"
      : "DST";
  const realPrefab = hasRealPrefab(item);
  const category = categoryLabel[item.category];

  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeButtonRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key !== "Tab") return;

      const focusable = Array.from(
        dialogRef.current?.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR) ?? [],
      );
      if (!focusable.length) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const shouldWrapBackward = event.shiftKey && document.activeElement === first;
      const shouldWrapForward = !event.shiftKey && document.activeElement === last;

      if (shouldWrapBackward || shouldWrapForward) {
        event.preventDefault();
        (shouldWrapBackward ? last : first).focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
      if (previouslyFocused?.isConnected) previouslyFocused.focus();
    };
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex cursor-pointer items-end justify-center bg-[#0f1d30]/55 p-0 backdrop-blur-[2px] sm:items-center sm:p-6"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="max-h-[92vh] w-full cursor-default overflow-y-auto rounded-t-3xl border border-[#c8d3df] bg-[#edf1f5] shadow-[0_28px_80px_rgba(15,29,48,0.32)] sm:max-w-4xl sm:rounded-3xl"
      >
        <div className="sticky top-0 z-10 flex items-start gap-4 border-b border-[#d5dde6] bg-[#f8fafc]/95 p-5 backdrop-blur sm:p-6">
          <GameSprite
            sprite={item.sprite}
            size={88}
            label={`Ảnh ${item.name}`}
            className="ring-1 ring-[#c8d3df]"
          />
          <div className="min-w-0 flex-1">
            <h2 id={titleId} className="text-xl font-semibold text-[#172943] sm:text-2xl">
              {item.name}
            </h2>
            {item.englishName ? (
              <p className="mt-1 text-sm text-[#607188]">{item.englishName}</p>
            ) : null}
            <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold">
              <span className="rounded-full border border-[#c8d3df] bg-[#eef3f8] px-2.5 py-1 text-[#43556d]">
                {category}
              </span>
              <span className="rounded-full border border-[#b9cce8] bg-[#e9f1fb] px-2.5 py-1 text-[#2e5fb3]">
                {sourceLabel}
              </span>
            </div>
          </div>
          <button
            ref={closeButtonRef}
            type="button"
            aria-label="Đóng chi tiết"
            onClick={onClose}
            className="inline-flex min-h-11 min-w-11 shrink-0 cursor-pointer items-center justify-center rounded-xl border border-[#c8d3df] text-[#53647a] transition hover:border-[#2e5fb3] hover:bg-[#e9eff6] hover:text-[#2e5fb3] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/30 active:scale-[0.98]"
          >
            <X aria-hidden="true" size={20} />
          </button>
        </div>

        <div className="space-y-4 p-5 sm:p-6">
          {item.description ? (
            <section
              aria-labelledby={`${titleId}-description`}
              className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]"
            >
              <h3
                id={`${titleId}-description`}
                className="border-b border-[#d5dde6] px-4 py-3 text-sm font-semibold text-[#172943]"
              >
                Mô tả
              </h3>
              <p className="px-4 py-3 text-sm leading-6 text-[#53647a]">
                {item.description}
              </p>
            </section>
          ) : null}

          {item.recipe ? (
            <section
              aria-labelledby={`${titleId}-crafting`}
              className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]"
            >
              <h3
                id={`${titleId}-crafting`}
                className="border-b border-[#d5dde6] px-4 py-3 text-sm font-semibold text-[#172943]"
              >
                Công thức
              </h3>
              <div className="flex flex-wrap items-center gap-3 p-4">
                <RecipeIngredients recipe={item.recipe} />
                <span aria-hidden="true" className="text-lg font-semibold text-[#607188]">
                  =
                </span>
                <span
                  aria-label={`Kết quả: ${item.name}, số lượng ${item.recipe.outputCount}`}
                  className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-[#b9cce8] bg-[#e9f1fb] py-1 pl-1 pr-3 text-sm font-semibold text-[#263b58]"
                >
                  <GameSprite sprite={item.sprite} size={32} />
                  <span>{item.name}</span>
                  {item.recipe.outputCount > 1 ? <span>×{item.recipe.outputCount}</span> : null}
                </span>
              </div>
              {item.craftingNote ? (
                <p className="border-t border-[#dce3eb] px-4 py-3 text-sm leading-6 text-[#53647a]">
                  {item.craftingNote}
                </p>
              ) : null}
            </section>
          ) : null}

          {!item.recipe && item.craftingNote ? (
            <section
              aria-labelledby={`${titleId}-crafting-note`}
              className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]"
            >
              <h3
                id={`${titleId}-crafting-note`}
                className="border-b border-[#d5dde6] px-4 py-3 text-sm font-semibold text-[#172943]"
              >
                Cách tạo / ghi chú chế tạo
              </h3>
              <p className="px-4 py-3 text-sm leading-6 text-[#53647a]">
                {item.craftingNote}
              </p>
            </section>
          ) : null}

          <section
            aria-labelledby={`${titleId}-technical`}
            className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]"
          >
            <h3
              id={`${titleId}-technical`}
              className="border-b border-[#d5dde6] px-4 py-3 text-sm font-semibold text-[#172943]"
            >
              Thông tin kỹ thuật
            </h3>
            <dl className="divide-y divide-[#dce3eb]">
              <div className="flex items-center justify-between gap-4 px-4 py-3 text-sm">
                <dt className="text-[#607188]">
                  {realPrefab ? "Prefab ID" : "Wiki page"}
                </dt>
                <dd className="max-w-[60%] truncate font-mono text-xs font-semibold text-[#263b58]">
                  {realPrefab ? item.prefabId : item.wiki?.pageId}
                </dd>
              </div>
              {item.wiki ? (
                <div className="flex items-center justify-between gap-4 px-4 py-3 text-sm">
                  <dt className="text-[#607188]">Trạng thái mapping</dt>
                  <dd className="font-semibold text-[#263b58]">
                    {item.wiki.mappingState === "mapped" ? "Đã map Prefab" : "Wiki độc lập"}
                  </dd>
                </div>
              ) : null}
            </dl>
          </section>

          {item.wiki?.relatedPages.length ? (
            <section
              aria-labelledby={`${titleId}-related`}
              className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]"
            >
              <h3
                id={`${titleId}-related`}
                className="border-b border-[#d5dde6] px-4 py-3 text-sm font-semibold text-[#172943]"
              >
                Trang liên quan
              </h3>
              <div className="flex flex-wrap gap-2 p-4">
                {item.wiki.relatedPages.map((page) => (
                  <a
                    key={page.pageId}
                    href={page.canonicalUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex min-h-11 items-center rounded-xl border border-[#b9cce8] px-3 py-2 text-sm font-semibold text-[#2e5fb3] hover:bg-[#e9f1fb]"
                  >
                    {page.title}
                  </a>
                ))}
              </div>
            </section>
          ) : null}

          {item.wiki ? (
            <WikiArticle
              key={item.wiki.detailUrl}
              detailUrl={item.wiki.detailUrl}
              canonicalUrl={item.wiki.canonicalUrl}
            />
          ) : null}
        </div>
      </section>
    </div>
  );
}
