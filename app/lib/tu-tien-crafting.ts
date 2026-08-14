import type { ItemListEntry } from "./item-catalog";

const HAN_LAP_BUILDER_TAGS = new Set(["player", "xd_hantianzun"]);

export type CraftingExclusionReason =
  | "no_recipe"
  | "other_character"
  | "no_verified_use"
  | "unresolved_ingredient";

export type HanLapCraftingSelection = {
  items: readonly ItemListEntry[];
  excluded: readonly {
    id: string;
    reason: CraftingExclusionReason;
  }[];
};

type RuntimeRecipe = {
  restrictions?: {
    builder_tags?: unknown;
  };
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function runtimeRecipesByItem(catalogPayload: unknown): ReadonlyMap<string, readonly RuntimeRecipe[]> {
  if (!isRecord(catalogPayload) || !Array.isArray(catalogPayload.entities)) {
    return new Map();
  }

  const recipesByItem = new Map<string, readonly RuntimeRecipe[]>();
  for (const entity of catalogPayload.entities) {
    if (!isRecord(entity) || typeof entity.key !== "string" || !Array.isArray(entity.recipes)) {
      continue;
    }
    recipesByItem.set(entity.key, entity.recipes.filter(isRecord));
  }
  return recipesByItem;
}

function recipeBuilderTags(recipe: RuntimeRecipe): readonly string[] {
  const tags = recipe.restrictions?.builder_tags;
  return Array.isArray(tags) && tags.every((tag) => typeof tag === "string") ? tags : [];
}

function hasAllowedRuntimeRecipe(recipes: readonly RuntimeRecipe[]): boolean {
  return recipes.some((recipe) =>
    recipeBuilderTags(recipe).every((tag) => HAN_LAP_BUILDER_TAGS.has(tag)),
  );
}

function hasResolvedRecipe(item: ItemListEntry, itemsById: ReadonlyMap<string, ItemListEntry>): boolean {
  return item.recipe !== null && item.recipe.ingredients.every((ingredient) => itemsById.has(ingredient.id));
}

function hasDocumentedMobMechanics(item: ItemListEntry): boolean {
  return item.mob?.contract === "catalog" && item.mob.mechanics.length > 0;
}

function isReferencedByResolvedRecipe(
  item: ItemListEntry,
  items: readonly ItemListEntry[],
  itemsById: ReadonlyMap<string, ItemListEntry>,
): boolean {
  return items.some(
    (candidate) =>
      hasResolvedRecipe(candidate, itemsById) &&
      candidate.recipe?.ingredients.some((ingredient) => ingredient.id === item.id),
  );
}

function hasVerifiedUse(
  item: ItemListEntry,
  items: readonly ItemListEntry[],
  itemsById: ReadonlyMap<string, ItemListEntry>,
): boolean {
  return (
    item.details?.usage.status === "known" ||
    item.structureDetails?.functions.status === "known" ||
    hasDocumentedMobMechanics(item) ||
    isReferencedByResolvedRecipe(item, items, itemsById)
  );
}

export function selectHanLapCraftables(
  items: readonly ItemListEntry[],
  catalogPayload: unknown,
): HanLapCraftingSelection {
  const itemsById = new Map(items.map((item) => [item.id, item]));
  const recipesByItem = runtimeRecipesByItem(catalogPayload);
  const selected: ItemListEntry[] = [];
  const excluded: { id: string; reason: CraftingExclusionReason }[] = [];

  for (const item of items) {
    if (item.namespace !== "tu_tien") continue;

    if (item.recipe === null) {
      excluded.push({ id: item.id, reason: "no_recipe" });
      continue;
    }
    if (!hasResolvedRecipe(item, itemsById)) {
      excluded.push({ id: item.id, reason: "unresolved_ingredient" });
      continue;
    }

    const runtimeRecipes = recipesByItem.get(item.id) ?? [];
    if (runtimeRecipes.length > 0 && !hasAllowedRuntimeRecipe(runtimeRecipes)) {
      excluded.push({ id: item.id, reason: "other_character" });
      continue;
    }
    if (!hasVerifiedUse(item, items, itemsById)) {
      excluded.push({ id: item.id, reason: "no_verified_use" });
      continue;
    }

    selected.push(item);
  }

  selected.sort(
    (left, right) =>
      left.category.localeCompare(right.category) ||
      left.name.localeCompare(right.name, "vi") ||
      left.id.localeCompare(right.id),
  );

  return { items: selected, excluded };
}
