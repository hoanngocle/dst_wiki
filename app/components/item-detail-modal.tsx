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
              Chi tiết {item.name}
            </h2>
            {item.englishName ? (
              <p className="mt-1 text-sm text-[#607188]">{item.englishName}</p>
            ) : null}
            <div className="mt-2 flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1 text-xs">
              <span className="font-semibold text-[#2e5fb3]">{sourceLabel}</span>
              <code className="truncate font-mono text-[11px] text-[#68798e]">
                {item.prefabId}
              </code>
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

        <div className="space-y-6 p-5 sm:p-6">
          <section aria-labelledby={`${titleId}-description`}>
            <h3
              id={`${titleId}-description`}
              className="text-sm font-semibold text-[#43556d]"
            >
              Mô tả
            </h3>
            <p className="mt-2 text-sm leading-6 text-[#53647a]">
              {item.description ?? "Chưa có mô tả."}
            </p>
          </section>

          <section
            aria-labelledby={`${titleId}-recipe`}
            className="border-t border-[#d5dde6] pt-5"
          >
            <h3 id={`${titleId}-recipe`} className="mb-3 text-sm font-semibold text-[#43556d]">
              Công thức
            </h3>
            <RecipeIngredients recipe={item.recipe} />
          </section>
        </div>
      </section>
    </div>
  );
}
