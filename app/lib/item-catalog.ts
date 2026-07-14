export type ItemNamespace = "tu_tien" | "base_game";
export type ItemFilter = "all" | ItemNamespace | "craftable";

export type SpriteDescriptor = {
  src: string;
  uv: {
    u1: number;
    u2: number;
    v1: number;
    v2: number;
  };
};

export type RecipeIngredient = {
  id: string;
  name: string;
  amount: number;
  sprite: SpriteDescriptor | null;
};

export type ItemRecipe = {
  outputCount: number;
  ingredients: readonly RecipeIngredient[];
};

export type ItemListEntry = {
  id: string;
  prefabId: string;
  namespace: ItemNamespace;
  name: string;
  englishName: string | null;
  description: string | null;
  sprite: SpriteDescriptor | null;
  recipe: ItemRecipe | null;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function requiredString(value: unknown, field: string): string {
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`${field} must be a non-empty string`);
  }
  return value;
}

function nullableString(value: unknown, field: string): string | null {
  if (value === null) return null;
  return requiredString(value, field);
}

function positiveInteger(value: unknown, field: string): number {
  if (typeof value !== "number" || !Number.isInteger(value) || value <= 0) {
    throw new Error(`${field} must be a positive integer`);
  }
  return value;
}

function parseSprite(value: unknown, field: string): SpriteDescriptor | null {
  if (value === null) return null;
  if (!isRecord(value) || !isRecord(value.uv)) {
    throw new Error(`${field} sprite must contain UV coordinates`);
  }
  const coordinates = [value.uv.u1, value.uv.u2, value.uv.v1, value.uv.v2];
  if (
    coordinates.some(
      (coordinate) =>
        typeof coordinate !== "number" ||
        !Number.isFinite(coordinate) ||
        coordinate < 0 ||
        coordinate > 1,
    ) ||
    (value.uv.u1 as number) >= (value.uv.u2 as number) ||
    (value.uv.v1 as number) >= (value.uv.v2 as number)
  ) {
    throw new Error(`${field} sprite has invalid UV coordinates`);
  }
  return {
    src: requiredString(value.src, `${field} sprite src`),
    uv: {
      u1: value.uv.u1 as number,
      u2: value.uv.u2 as number,
      v1: value.uv.v1 as number,
      v2: value.uv.v2 as number,
    },
  };
}

function parseIngredient(value: unknown, index: number): RecipeIngredient {
  if (!isRecord(value)) {
    throw new Error(`ingredient ${index} must be an object`);
  }
  return {
    id: requiredString(value.id, `ingredient ${index} id`),
    name: requiredString(value.name, `ingredient ${index} name`),
    amount: positiveInteger(value.amount, `ingredient amount at index ${index}`),
    sprite: parseSprite(value.sprite, `ingredient ${index}`),
  };
}

function parseRecipe(value: unknown, itemIndex: number): ItemRecipe | null {
  if (value === null) return null;
  if (!isRecord(value) || !Array.isArray(value.ingredients)) {
    throw new Error(`item ${itemIndex} recipe must contain ingredients`);
  }
  return {
    outputCount: positiveInteger(value.outputCount, `item ${itemIndex} recipe output`),
    ingredients: value.ingredients.map(parseIngredient),
  };
}

function parseItem(value: unknown, index: number): ItemListEntry {
  if (!isRecord(value)) {
    throw new Error(`item ${index} must be an object`);
  }
  if (value.namespace !== "tu_tien" && value.namespace !== "base_game") {
    throw new Error(`item ${index} namespace is invalid`);
  }
  return {
    id: requiredString(value.id, `item ${index} id`),
    prefabId: requiredString(value.prefabId, `item ${index} prefabId`),
    namespace: value.namespace,
    name: requiredString(value.name, `item ${index} name`),
    englishName: nullableString(value.englishName, `item ${index} englishName`),
    description: nullableString(value.description, `item ${index} description`),
    sprite: parseSprite(value.sprite, `item ${index}`),
    recipe: parseRecipe(value.recipe, index),
  };
}

export function parseItemPayload(value: unknown): readonly ItemListEntry[] {
  if (
    !isRecord(value) ||
    value.schema_version !== 1 ||
    !Array.isArray(value.items)
  ) {
    throw new Error("item payload must use schema version 1 and contain items");
  }
  return value.items.map(parseItem);
}
