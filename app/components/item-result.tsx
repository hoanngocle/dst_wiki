import { Package } from "@phosphor-icons/react";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { findNormalizedTextMatch } from "@/app/lib/wiki-search";
import { GameSprite } from "./game-sprite";
import { RecipeIngredients } from "./recipe-ingredients";

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

export function ItemResult({ item, query }: { item: ItemListEntry; query: string }) {
  const sourceLabel = item.namespace === "tu_tien" ? "Tu Tiên" : "DST gốc liên quan";

  return (
    <article className="h-full rounded-2xl border border-[#c8d3df] bg-[#f8fafc] p-4 shadow-[0_12px_32px_rgba(40,66,98,0.07)] transition duration-200 hover:-translate-y-0.5 hover:border-[#9fb3cb] hover:shadow-[0_16px_36px_rgba(40,66,98,0.11)] motion-reduce:transform-none motion-reduce:transition-none sm:p-5">
      <div className="grid grid-cols-[44px_64px_minmax(0,1fr)] items-center gap-3">
        <span
          aria-label="Loại: Item"
          className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-[#dce6f4] text-[#2e5fb3]"
        >
          <Package aria-hidden="true" size={22} weight="duotone" />
        </span>
        <GameSprite sprite={item.sprite} size={64} className="ring-1 ring-[#c8d3df]" />
        <div className="min-w-0">
          <h3 className="truncate text-base font-semibold text-[#172943]">
            <HighlightedText text={item.name} query={query} />
          </h3>
          <div className="mt-1 flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1 text-xs text-[#607188]">
            <span className="font-medium text-[#2e5fb3]">{sourceLabel}</span>
            <code className="truncate font-mono text-[11px] text-[#68798e]">{item.prefabId}</code>
          </div>
        </div>
      </div>

      {item.description ? (
        <p className="mt-3 line-clamp-2 text-sm leading-6 text-[#53647a]">
          <HighlightedText text={item.description} query={query} />
        </p>
      ) : null}

      <div className="mt-4 border-t border-[#d5dde6] pt-3">
        <p className="mb-2 text-xs font-semibold text-[#43556d]">Công thức</p>
        <RecipeIngredients recipe={item.recipe} />
      </div>
    </article>
  );
}
