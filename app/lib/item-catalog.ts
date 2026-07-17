export type ItemNamespace = "tu_tien" | "base_game";
export type ItemSourceFilter = "all" | "wiki" | ItemNamespace;
export type ItemAvailabilityFilter = "all" | "recipe" | "image";
export type PrefabCategory =
  | "item"
  | "mob"
  | "boss"
  | "character"
  | "structure"
  | "effect"
  | "other";
export type PrefabCategoryFilter = "all" | PrefabCategory;

export type CatalogSummary = {
  total: number;
  wiki: number;
  recipes: number;
  pictured: number;
};

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

export type ItemDetailStatus = "known" | "none" | "unknown";

export type ItemEvidence = {
  source: string;
  locator: string | null;
};

export type ItemReference = {
  id: string;
  name: string;
  sprite: SpriteDescriptor | null;
};

export type ItemUsageRecipe = {
  result: ItemReference;
  resultAmount: number;
  subjectAmount: number;
  ingredients: readonly RecipeIngredient[];
  craftingNote: string | null;
};

export type ItemUsageEffect = {
  trigger: string;
  text: string;
  evidence: readonly ItemEvidence[];
};

export type ItemDropSource = {
  type: "drop" | "harvest" | "start" | "trade" | "other";
  source: ItemReference | null;
  quantity: string | null;
  chance: string | null;
  conditions: string | null;
  evidence: readonly ItemEvidence[];
};

export type ItemDetails = {
  recipeStatus: ItemDetailStatus;
  usage: {
    status: ItemDetailStatus;
    recipes: readonly ItemUsageRecipe[];
    effects: readonly ItemUsageEffect[];
  };
  dropBy: {
    status: ItemDetailStatus;
    sources: readonly ItemDropSource[];
  };
};

export type WikiRelatedPage = {
  pageId: number;
  title: string;
  canonicalUrl: string;
  detailUrl: string;
};

export type WikiItemMetadata = {
  pageId: number;
  title: string;
  canonicalUrl: string;
  categories: readonly string[];
  mappingState: "mapped" | "unmatched";
  detailUrl: string;
  relatedPages: readonly WikiRelatedPage[];
};

export type ItemListEntry = {
  id: string;
  prefabId: string;
  namespace: ItemNamespace;
  category: PrefabCategory;
  name: string;
  englishName: string | null;
  description: string | null;
  craftingNote: string | null;
  sprite: SpriteDescriptor | null;
  recipe: ItemRecipe | null;
  details: ItemDetails | null;
  wiki: WikiItemMetadata | null;
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

function parseCategory(value: unknown, itemIndex: number): PrefabCategory {
  if (
    value !== "item" &&
    value !== "mob" &&
    value !== "boss" &&
    value !== "character" &&
    value !== "structure" &&
    value !== "effect" &&
    value !== "other"
  ) {
    throw new Error(`item ${itemIndex} category is invalid`);
  }
  return value;
}

function positiveInteger(value: unknown, field: string): number {
  if (typeof value !== "number" || !Number.isInteger(value) || value <= 0) {
    throw new Error(`${field} must be a positive integer`);
  }
  return value;
}

function positiveNumber(value: unknown, field: string): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value <= 0) {
    throw new Error(`${field} must be a positive number`);
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
    amount: positiveNumber(value.amount, `ingredient amount at index ${index}`),
    sprite: parseSprite(value.sprite, `ingredient ${index}`),
  };
}

function parseRelatedPage(value: unknown, index: number): WikiRelatedPage {
  if (!isRecord(value)) {
    throw new Error(`wiki related page ${index} must be an object`);
  }
  return {
    pageId: positiveInteger(value.pageId, `wiki related page ${index} pageId`),
    title: requiredString(value.title, `wiki related page ${index} title`),
    canonicalUrl: requiredString(
      value.canonicalUrl,
      `wiki related page ${index} canonicalUrl`,
    ),
    detailUrl: requiredString(value.detailUrl, `wiki related page ${index} detailUrl`),
  };
}

function parseWiki(value: unknown, itemIndex: number): WikiItemMetadata | null {
  if (value === null) return null;
  if (!isRecord(value) || !Array.isArray(value.categories) || !Array.isArray(value.relatedPages)) {
    throw new Error(`item ${itemIndex} wiki metadata is invalid`);
  }
  if (value.mappingState !== "mapped" && value.mappingState !== "unmatched") {
    throw new Error(`item ${itemIndex} wiki mappingState is invalid`);
  }
  return {
    pageId: positiveInteger(value.pageId, `item ${itemIndex} wiki pageId`),
    title: requiredString(value.title, `item ${itemIndex} wiki title`),
    canonicalUrl: requiredString(
      value.canonicalUrl,
      `item ${itemIndex} wiki canonicalUrl`,
    ),
    categories: value.categories.map((category, categoryIndex) =>
      requiredString(category, `item ${itemIndex} wiki category ${categoryIndex}`),
    ),
    mappingState: value.mappingState,
    detailUrl: requiredString(value.detailUrl, `item ${itemIndex} wiki detailUrl`),
    relatedPages: value.relatedPages.map(parseRelatedPage),
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

function parseDetailStatus(value: unknown, field: string): ItemDetailStatus {
  if (value !== "known" && value !== "none" && value !== "unknown") {
    throw new Error(`${field} status is invalid`);
  }
  return value;
}

function parseEvidence(value: unknown, field: string): readonly ItemEvidence[] {
  if (!Array.isArray(value) || !value.length) {
    throw new Error(`${field} evidence must be a non-empty array`);
  }
  return value.map((entry, index) => {
    if (!isRecord(entry)) {
      throw new Error(`${field} evidence ${index} must be an object`);
    }
    return {
      source: requiredString(entry.source, `${field} evidence ${index} source`),
      locator: nullableString(entry.locator, `${field} evidence ${index} locator`),
    };
  });
}

function parseReference(value: unknown, field: string): ItemReference {
  if (!isRecord(value)) {
    throw new Error(`${field} reference must be an object`);
  }
  return {
    id: requiredString(value.id, `${field} id`),
    name: requiredString(value.name, `${field} name`),
    sprite: parseSprite(value.sprite, field),
  };
}

function parseUsageRecipe(value: unknown, index: number): ItemUsageRecipe {
  if (!isRecord(value) || !Array.isArray(value.ingredients)) {
    throw new Error(`usage recipe ${index} must contain ingredients`);
  }
  return {
    result: parseReference(value.result, `usage recipe ${index} result`),
    resultAmount: positiveNumber(
      value.resultAmount,
      `usage recipe ${index} result amount`,
    ),
    subjectAmount: positiveNumber(
      value.subjectAmount,
      `usage recipe ${index} subject amount`,
    ),
    ingredients: value.ingredients.map(parseIngredient),
    craftingNote: nullableString(
      value.craftingNote,
      `usage recipe ${index} craftingNote`,
    ),
  };
}

function parseUsageEffect(value: unknown, index: number): ItemUsageEffect {
  if (!isRecord(value)) {
    throw new Error(`usage effect ${index} must be an object`);
  }
  return {
    trigger: requiredString(value.trigger, `usage effect ${index} trigger`),
    text: requiredString(value.text, `usage effect ${index} text`),
    evidence: parseEvidence(value.evidence, `usage effect ${index}`),
  };
}

function parseDropSource(value: unknown, index: number): ItemDropSource {
  if (!isRecord(value)) {
    throw new Error(`drop source ${index} must be an object`);
  }
  if (
    value.type !== "drop" &&
    value.type !== "harvest" &&
    value.type !== "start" &&
    value.type !== "trade" &&
    value.type !== "other"
  ) {
    throw new Error(`drop source type at index ${index} is invalid`);
  }
  return {
    type: value.type,
    source:
      value.source === null
        ? null
        : parseReference(value.source, `drop source ${index}`),
    quantity: nullableString(value.quantity, `drop source ${index} quantity`),
    chance: nullableString(value.chance, `drop source ${index} chance`),
    conditions: nullableString(
      value.conditions,
      `drop source ${index} conditions`,
    ),
    evidence: parseEvidence(value.evidence, `drop source ${index}`),
  };
}

function parseDetails(
  value: unknown,
  namespace: ItemNamespace,
  itemIndex: number,
): ItemDetails | null {
  if (namespace === "base_game") {
    if (value !== null) {
      throw new Error(`base-game item ${itemIndex} details must be null`);
    }
    return null;
  }
  if (!isRecord(value) || !isRecord(value.usage) || !isRecord(value.dropBy)) {
    throw new Error(`Tu Tiên item ${itemIndex} details must be an object`);
  }
  if (!Array.isArray(value.usage.recipes) || !Array.isArray(value.usage.effects)) {
    throw new Error(`item ${itemIndex} usage details must contain arrays`);
  }
  if (!Array.isArray(value.dropBy.sources)) {
    throw new Error(`item ${itemIndex} dropBy details must contain sources`);
  }
  const usageStatus = parseDetailStatus(
    value.usage.status,
    `item ${itemIndex} usage`,
  );
  const usageRecipes = value.usage.recipes.map(parseUsageRecipe);
  const usageEffects = value.usage.effects.map(parseUsageEffect);
  if (usageStatus === "known" && !usageRecipes.length && !usageEffects.length) {
    throw new Error(`item ${itemIndex} known usage section must contain data`);
  }
  const dropStatus = parseDetailStatus(
    value.dropBy.status,
    `item ${itemIndex} dropBy`,
  );
  const dropSources = value.dropBy.sources.map(parseDropSource);
  if (dropStatus === "known" && !dropSources.length) {
    throw new Error(`item ${itemIndex} known dropBy section must contain data`);
  }
  return {
    recipeStatus: parseDetailStatus(
      value.recipeStatus,
      `item ${itemIndex} recipe`,
    ),
    usage: {
      status: usageStatus,
      recipes: usageRecipes,
      effects: usageEffects,
    },
    dropBy: { status: dropStatus, sources: dropSources },
  };
}

function parseItem(value: unknown, index: number): ItemListEntry {
  if (!isRecord(value)) {
    throw new Error(`item ${index} must be an object`);
  }
  if (value.namespace !== "tu_tien" && value.namespace !== "base_game") {
    throw new Error(`item ${index} namespace is invalid`);
  }
  const namespace = value.namespace;
  return {
    id: requiredString(value.id, `item ${index} id`),
    prefabId: requiredString(value.prefabId, `item ${index} prefabId`),
    namespace,
    category: parseCategory(value.category, index),
    name: requiredString(value.name, `item ${index} name`),
    englishName: nullableString(value.englishName, `item ${index} englishName`),
    description: nullableString(value.description, `item ${index} description`),
    craftingNote: nullableString(value.craftingNote, `item ${index} craftingNote`),
    sprite: parseSprite(value.sprite, `item ${index}`),
    recipe: parseRecipe(value.recipe, index),
    details: parseDetails(value.details, namespace, index),
    wiki: parseWiki(value.wiki, index),
  };
}

function catalogKey(item: Pick<ItemListEntry, "namespace" | "prefabId">): string {
  return `${item.namespace}:${item.prefabId}`;
}

function curateItems(items: readonly ItemListEntry[]): ItemListEntry[] {
  const candidates = items.filter((item) => !item.prefabId.endsWith("_fx"));
  const itemsByKey = new Map(candidates.map((item) => [catalogKey(item), item]));

  return candidates.filter((item) => {
    if (item.prefabId.endsWith("_item")) {
      const basePrefabId = item.prefabId.slice(0, -"_item".length);
      const baseItem = itemsByKey.get(
        catalogKey({ namespace: item.namespace, prefabId: basePrefabId }),
      );
      return !baseItem || item.sprite !== null;
    }

    const itemVariant = itemsByKey.get(
      catalogKey({ namespace: item.namespace, prefabId: `${item.prefabId}_item` }),
    );
    return !itemVariant || itemVariant.sprite === null;
  });
}

export function parseItemPayload(value: unknown): readonly ItemListEntry[] {
  if (
    !isRecord(value) ||
    value.schema_version !== 5 ||
    !Array.isArray(value.items)
  ) {
    throw new Error("item payload must use schema version 5 and contain items");
  }
  return curateItems(value.items.map(parseItem));
}
