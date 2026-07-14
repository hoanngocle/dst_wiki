import type { ItemRecipe } from "@/app/lib/item-catalog";
import { GameSprite } from "./game-sprite";

export function RecipeIngredients({ recipe }: { recipe: ItemRecipe | null }) {
  if (!recipe) {
    return <p className="text-sm text-[#66768b]">Không có công thức</p>;
  }

  if (recipe.ingredients.length === 0) {
    return <p className="text-sm font-medium text-[#53647a]">Công thức đặc biệt</p>;
  }

  return (
    <div className="flex flex-wrap items-center gap-2" aria-label="Nguyên liệu chế tạo">
      {recipe.ingredients.map((ingredient) => (
        <span
          key={ingredient.id}
          aria-label={`${ingredient.name}, số lượng ${ingredient.amount}`}
          className="inline-flex min-h-10 items-center gap-1.5 rounded-xl border border-[#c8d3df] bg-[#f8fafc] py-1 pl-1 pr-2.5 text-sm font-semibold text-[#263b58]"
          title={ingredient.name}
        >
          <GameSprite sprite={ingredient.sprite} size={32} />
          <span aria-hidden="true">×{ingredient.amount}</span>
        </span>
      ))}
    </div>
  );
}
