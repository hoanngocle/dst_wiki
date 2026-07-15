import {
  Bug,
  Buildings,
  Crown,
  Package,
  Question,
  Sparkle,
  User,
  type Icon,
} from "@phosphor-icons/react";

import type {
  ItemListEntry,
  PrefabCategory,
} from "@/app/lib/item-catalog";
import { findNormalizedTextMatch } from "@/app/lib/wiki-search";
import { GameSprite } from "./game-sprite";
import { RecipeIngredients } from "./recipe-ingredients";

const categoryMetadata: Record<
  PrefabCategory,
  { label: string; icon: Icon }
> = {
  item: { label: "Item", icon: Package },
  mob: { label: "Mob", icon: Bug },
  boss: { label: "Boss", icon: Crown },
  character: { label: "Nhân vật", icon: User },
  structure: { label: "Công trình", icon: Buildings },
  effect: { label: "Hiệu ứng", icon: Sparkle },
  other: { label: "Khác", icon: Question },
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

type ItemResultProps = {
  item: ItemListEntry;
  query: string;
  itemsById?: ReadonlyMap<string, ItemListEntry>;
  onSelectItem?: (item: ItemListEntry) => void;
};

export function ItemResult({
  item,
  query,
  itemsById,
  onSelectItem,
}: ItemResultProps) {
  const sourceLabel = item.namespace === "tu_tien" ? "Tu Tiên" : "DST gốc liên quan";
  const category = categoryMetadata[item.category];
  const CategoryIcon = category.icon;

  return (
    <article className="h-full rounded-2xl border border-[#c8d3df] bg-[#f8fafc] p-4 shadow-[0_12px_32px_rgba(40,66,98,0.07)] transition duration-200 hover:-translate-y-0.5 hover:border-[#9fb3cb] hover:shadow-[0_16px_36px_rgba(40,66,98,0.11)] motion-reduce:transform-none motion-reduce:transition-none sm:p-5">
      <button
        type="button"
        disabled={!onSelectItem}
        aria-label={`Xem chi tiết ${item.name}`}
        onClick={() => onSelectItem?.(item)}
        className="block w-full cursor-pointer rounded-xl text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/30 disabled:cursor-default"
      >
        <div className="grid grid-cols-[64px_minmax(0,1fr)] items-center gap-3">
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
          <span
            aria-label={`Loại: ${category.label}`}
            className="col-span-2 inline-flex w-fit items-center gap-1.5 rounded-full border border-[#c8d3df] bg-[#eef3f8] px-2.5 py-1 text-xs font-medium text-[#43556d]"
          >
            <CategoryIcon aria-hidden="true" size={15} weight="duotone" />
            {category.label}
          </span>
        </div>

        {item.description ? (
          <p className="mt-3 line-clamp-2 text-sm leading-6 text-[#53647a]">
            <HighlightedText text={item.description} query={query} />
          </p>
        ) : null}
      </button>

      <div className="mt-4 border-t border-[#d5dde6] pt-3">
        <p className="mb-2 text-xs font-semibold text-[#43556d]">Công thức</p>
        <RecipeIngredients
          recipe={item.recipe}
          itemsById={itemsById}
          onSelectItem={onSelectItem}
        />
      </div>
    </article>
  );
}
