import { X } from "@phosphor-icons/react";
import { useEffect, useId, useRef } from "react";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { GameSprite } from "./game-sprite";
import { RecipeIngredients } from "./recipe-ingredients";

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
  const sourceLabel = item.namespace === "tu_tien" ? "Tu Tiên" : "DST gốc liên quan";
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
      className="fixed inset-0 z-50 flex items-end justify-center bg-[#0f1d30]/55 p-0 backdrop-blur-[2px] sm:items-center sm:p-6"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="max-h-[90vh] w-full overflow-y-auto rounded-t-3xl border border-[#c8d3df] bg-[#f8fafc] shadow-[0_28px_80px_rgba(15,29,48,0.32)] sm:max-w-2xl sm:rounded-3xl"
      >
        <div className="flex items-start gap-4 border-b border-[#d5dde6] p-5 sm:p-6">
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
            className="inline-flex min-h-11 min-w-11 shrink-0 items-center justify-center rounded-xl border border-[#c8d3df] text-[#53647a] transition hover:border-[#2e5fb3] hover:bg-[#e9eff6] hover:text-[#2e5fb3] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/30 active:scale-[0.98]"
          >
            <X aria-hidden="true" size={20} />
          </button>
        </div>

        <div className="space-y-4 p-5 sm:p-6">
          <section
            aria-labelledby={`${titleId}-source`}
            className="overflow-hidden rounded-2xl border border-[#c8d3df]"
          >
            <h3
              id={`${titleId}-source`}
              className="bg-[#263b58] px-4 py-2 text-sm font-semibold text-[#f8fafc]"
            >
              Source
            </h3>
            <p className="px-4 py-3 text-sm font-medium text-[#607188]">Dropped by</p>
          </section>

          {item.recipe ? (
            <section
              aria-labelledby={`${titleId}-crafting`}
              className="overflow-hidden rounded-2xl border border-[#c8d3df]"
            >
              <h3
                id={`${titleId}-crafting`}
                className="bg-[#263b58] px-4 py-2 text-sm font-semibold text-[#f8fafc]"
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
            </section>
          ) : null}

          <section
            aria-labelledby={`${titleId}-miscellaneous`}
            className="overflow-hidden rounded-2xl border border-[#c8d3df]"
          >
            <h3
              id={`${titleId}-miscellaneous`}
              className="bg-[#263b58] px-4 py-2 text-sm font-semibold text-[#f8fafc]"
            >
              Miscellaneous
            </h3>
            <dl className="divide-y divide-[#dce3eb]">
              <div className="flex items-center justify-between gap-4 px-4 py-3 text-sm">
                <dt className="text-[#607188]">Prefab ID</dt>
                <dd className="max-w-[60%] truncate font-mono text-xs font-semibold text-[#263b58]">
                  {item.prefabId}
                </dd>
              </div>
            </dl>
          </section>
        </div>
      </section>
    </div>
  );
}
