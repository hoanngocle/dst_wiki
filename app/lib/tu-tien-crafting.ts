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
  builderTags: readonly string[];
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function runtimeRecipesByItem(catalogPayload: unknown): ReadonlyMap<string, readonly RuntimeRecipe[]> {
  if (!isRecord(catalogPayload) || !Array.isArray(catalogPayload.entities)) {
    throw new Error("Invalid crafting catalog: entities must be an array");
  }

  const recipesByItem = new Map<string, readonly RuntimeRecipe[]>();
  for (const [entityIndex, entity] of catalogPayload.entities.entries()) {
    const entityPath = `entities[${entityIndex}]`;
    if (!isRecord(entity)) {
      throw new Error(`Invalid crafting catalog: ${entityPath} must be an object`);
    }
    if (typeof entity.key !== "string" || entity.key.length === 0) {
      throw new Error(`Invalid crafting catalog: ${entityPath}.key must be a string`);
    }
    if (!Array.isArray(entity.recipes)) {
      throw new Error(`Invalid crafting catalog: ${entityPath}.recipes must be an array`);
    }
    const recipes = entity.recipes.map((recipe, recipeIndex): RuntimeRecipe => {
      const recipePath = `${entityPath}.recipes[${recipeIndex}]`;
      if (!isRecord(recipe)) {
        throw new Error(`Invalid crafting catalog: ${recipePath} must be an object`);
      }

      const restrictions = recipe.restrictions;
      if (restrictions !== undefined && !isRecord(restrictions)) {
        throw new Error(`Invalid crafting catalog: ${recipePath}.restrictions must be an object`);
      }

      const builderTags = restrictions?.builder_tags;
      if (
        builderTags !== undefined &&
        (!Array.isArray(builderTags) ||
          !builderTags.every((tag) => typeof tag === "string"))
      ) {
        throw new Error(
          `Invalid crafting catalog: ${recipePath}.restrictions.builder_tags must be an array of strings`,
        );
      }

      return { builderTags: builderTags ?? [] };
    });
    recipesByItem.set(entity.key, recipes);
  }
  return recipesByItem;
}

function hasAllowedRuntimeRecipe(recipes: readonly RuntimeRecipe[]): boolean {
  return recipes.some((recipe) =>
    recipe.builderTags.every((tag) => HAN_LAP_BUILDER_TAGS.has(tag)),
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
    (item.details?.usage.status === "known" &&
      (item.details.usage.recipes.length > 0 || item.details.usage.effects.length > 0)) ||
    (item.structureDetails?.functions.status === "known" &&
      item.structureDetails.functions.facts.length > 0) ||
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

    const runtimeRecipes = recipesByItem.get(item.id);
    if (!runtimeRecipes) {
      throw new Error(`Invalid crafting catalog: missing catalog entity for ${item.id}`);
    }
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
