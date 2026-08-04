import { useId } from "react";

import type { ItemListEntry, ItemRecipe } from "@/app/lib/item-catalog";
import { GameSprite } from "./game-sprite";

type RecipeIngredientsProps = {
  recipe: ItemRecipe | null;
  itemsById?: ReadonlyMap<string, ItemListEntry>;
  onSelectItem?: (item: ItemListEntry) => void;
};

export function RecipeIngredients({
  recipe,
  itemsById,
  onSelectItem,
}: RecipeIngredientsProps) {
  const tooltipPrefix = useId();

  if (!recipe) {
    return <p className="text-sm text-nova-muted">Không có công thức</p>;
  }

  if (recipe.ingredients.length === 0) {
    return <p className="text-sm font-medium text-nova-muted">Công thức đặc biệt</p>;
  }

  return (
    <div className="flex flex-wrap items-center gap-2" aria-label="Nguyên liệu chế tạo">
      {recipe.ingredients.map((ingredient, index) => {
        const fullItem = itemsById?.get(ingredient.id);
        const accessibleName = `${ingredient.name}, số lượng ${ingredient.amount}`;
        const content = (
          <>
            <GameSprite sprite={ingredient.sprite} size={32} />
            <span aria-hidden="true">×{ingredient.amount}</span>
          </>
        );

        if (fullItem && onSelectItem) {
          const tooltipId = `${tooltipPrefix}-${index}`;

          return (
            <button
              key={ingredient.id}
              type="button"
              aria-label={accessibleName}
              aria-describedby={tooltipId}
              onClick={() => onSelectItem(fullItem)}
              className="group relative inline-flex min-h-10 cursor-pointer items-center gap-1.5 rounded-xl border border-nova-border bg-nova-surface-soft py-1 pl-1 pr-2.5 text-sm font-semibold text-nova-text transition hover:border-nova-accent hover:bg-nova-surface-soft focus-visible:border-nova-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent active:scale-[0.98]"
            >
              {content}
              <span
                id={tooltipId}
                role="tooltip"
                className="pointer-events-none invisible absolute bottom-full left-1/2 z-20 mb-2 -translate-x-1/2 whitespace-nowrap rounded-lg bg-nova-text px-2.5 py-1.5 text-xs font-medium text-white opacity-0 shadow-lg transition group-hover:visible group-hover:opacity-100 group-focus-visible:visible group-focus-visible:opacity-100"
              >
                {ingredient.name}
              </span>
            </button>
          );
        }

        return (
          <span
            key={ingredient.id}
            aria-label={accessibleName}
            className="inline-flex min-h-10 items-center gap-1.5 rounded-xl border border-nova-border bg-nova-surface-soft py-1 pl-1 pr-2.5 text-sm font-semibold text-nova-text"
            title={ingredient.name}
          >
            {content}
          </span>
        );
      })}
    </div>
  );
}
