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
import { findNormalizedTextMatch, hasRealPrefab } from "@/app/lib/wiki-search";
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
  const sourceLabel = item.wiki
    ? "Wiki"
    : item.namespace === "tu_tien"
      ? "Tu Tiên"
      : "DST";
  const realPrefab = hasRealPrefab(item);
  const category = categoryMetadata[item.category];
  const CategoryIcon = category.icon;

  return (
    <article className="catalog-card h-full rounded-2xl border border-[#c8d3df] bg-[#f8fafc] p-4 shadow-[0_10px_28px_rgba(40,66,98,0.06)] transition duration-200 hover:-translate-y-0.5 hover:border-[#9fb3cb] hover:shadow-[0_14px_32px_rgba(40,66,98,0.1)] motion-reduce:transform-none motion-reduce:transition-none">
      <button
        type="button"
        disabled={!onSelectItem}
        aria-label={`Xem chi tiết ${item.name}`}
        onClick={() => onSelectItem?.(item)}
        className="block w-full cursor-pointer rounded-xl text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/30 disabled:cursor-default"
      >
        <div className="grid grid-cols-[72px_minmax(0,1fr)] items-center gap-3.5">
          <GameSprite sprite={item.sprite} size={72} className="ring-1 ring-[#c8d3df]" />
          <div className="min-w-0">
            <div className="mb-1.5 flex flex-wrap items-center gap-1.5 text-[11px] font-semibold">
              <span className="rounded-full border border-[#b9cce8] bg-[#e9f1fb] px-2 py-0.5 text-[#2e5fb3]">
                {sourceLabel}
              </span>
              <span
                aria-label={`Loại: ${category.label}`}
                className="inline-flex items-center gap-1 rounded-full border border-[#c8d3df] bg-[#eef3f8] px-2 py-0.5 text-[#43556d]"
              >
                <CategoryIcon aria-hidden="true" size={13} weight="duotone" />
                {category.label}
              </span>
            </div>
            <h3 className="truncate text-[17px] font-semibold text-[#172943]">
              <HighlightedText text={item.name} query={query} />
            </h3>
            {item.englishName ? (
              <p lang="en" className="mt-0.5 truncate text-sm text-[#607188]">
                {item.englishName}
              </p>
            ) : null}
            {realPrefab ? (
              <code className="mt-1 block truncate font-mono text-[11px] text-[#68798e]">
                {item.prefabId}
              </code>
            ) : (
              <span className="mt-1 block text-xs font-medium text-[#607188]">Wiki item</span>
            )}
          </div>
        </div>

        {item.description ? (
          <p className="mt-3 line-clamp-2 text-sm leading-6 text-[#53647a]">
            <HighlightedText text={item.description} query={query} />
          </p>
        ) : null}
      </button>

      {item.recipe ? (
        <div className="mt-4 border-t border-[#d5dde6] pt-3">
          <p className="mb-2 text-xs font-semibold text-[#43556d]">Công thức</p>
          <RecipeIngredients
            recipe={item.recipe}
            itemsById={itemsById}
            onSelectItem={onSelectItem}
          />
        </div>
      ) : null}
    </article>
  );
}
