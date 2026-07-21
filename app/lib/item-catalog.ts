export type ItemNamespace = "tu_tien" | "base_game";
export type ItemSourceFilter = "all" | ItemNamespace;
export type ItemAvailabilityFilter = "all" | "recipe" | "image";
export type PrefabCategory =
  | "item"
  | "pill"
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

export type MobStat = {
  key: string;
  label: string;
  value: string | number;
  unit: string | null;
  sourceVariant: string;
  evidence: readonly ItemEvidence[];
};

export type MobRewardMethod =
  | "kill"
  | "mine_post_defeat"
  | "harvest"
  | "conditional";

export type MobAppearance = {
  status: ItemDetailStatus;
  sources: readonly string[];
  spawnCodes: readonly string[];
  renewable: boolean | null;
  respawn: string | number | null;
  wikiUrl: string | null;
  evidence: readonly ItemEvidence[];
};

export type MobVariant = {
  id: string;
  prefabId: string;
  name: string;
  role: "phase" | "variant" | "summon" | "post_defeat";
  order: number;
  sprite: SpriteDescriptor | null;
};

export type MobMechanic = {
  text: string;
  sourceVariant: string;
  evidence: readonly ItemEvidence[];
};

export type MobLoot = {
  item: ItemReference;
  minimum: number;
  maximum: number;
  chance: string | null;
  method: MobRewardMethod;
  sourceVariant: string;
  lootTable: string | null;
  conditions: string | null;
  evidence: readonly ItemEvidence[];
};

export type MobDetails = {
  appearance: MobAppearance;
  variants: readonly MobVariant[];
  stats: readonly MobStat[];
  mechanics: readonly MobMechanic[];
  lootStatus: ItemDetailStatus;
  loot: readonly MobLoot[];
};

export type CharacterProfile = {
  title: string | null;
  survivability: string | null;
  quote: string | null;
  abilities: readonly string[];
};

export type StructureFunctionFact = {
  key: string;
  label: string;
  value: string;
  unit: string | null;
  context: string | null;
  related: readonly string[];
  evidence: readonly ItemEvidence[];
};

export type StructureStationRecipe = {
  result: ItemReference;
  resultAmount: number;
  ingredients: readonly RecipeIngredient[];
  station: string;
  tech: string | null;
  restrictions: Readonly<Record<string, unknown>>;
  note: string | null;
  evidence: readonly ItemEvidence[];
};

export type StructureVisualImage = {
  title: string | null;
  src: string;
  mime: string | null;
  width: number | null;
  height: number | null;
  evidence: readonly ItemEvidence[];
};

export type StructureDetails = {
  origin: {
    status: ItemDetailStatus;
    naturallySpawned: boolean;
    renewable: boolean | null;
    spawnCode: string | null;
    sources: readonly string[];
    respawn: string | null;
    craftable: boolean;
    note: string | null;
    evidence: readonly ItemEvidence[];
  };
  construction: {
    status: ItemDetailStatus;
    outputCount: number | null;
    ingredients: readonly RecipeIngredient[];
    tech: string | null;
    station: string | null;
    restrictions: Readonly<Record<string, unknown>>;
    note: string | null;
    evidence: readonly ItemEvidence[];
  };
  functions: {
    status: ItemDetailStatus;
    facts: readonly StructureFunctionFact[];
    reason: string | null;
    evidence: readonly ItemEvidence[];
  };
  craftables: {
    status: ItemDetailStatus;
    recipes: readonly StructureStationRecipe[];
    reason: string | null;
    evidence: readonly ItemEvidence[];
  };
  destruction: {
    status: ItemDetailStatus;
    destroyable: boolean | null;
    tool: string | null;
    work: string | null;
    health: string | null;
    burnable: boolean | null;
    drops: readonly unknown[];
    regeneration: string | null;
    evidence: readonly ItemEvidence[];
  };
  visual: {
    status: ItemDetailStatus;
    kind: "inventory_icon" | "wiki_image" | null;
    sprite: SpriteDescriptor | null;
    image: StructureVisualImage | null;
    alternatives: readonly Readonly<Record<string, unknown>>[];
    reason: string | null;
    evidence: readonly ItemEvidence[];
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
  details?: ItemDetails | null;
  mob?: MobDetails | null;
  character?: CharacterProfile | null;
  structureDetails?: StructureDetails | null;
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
    value !== "pill" &&
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

function parseMobEvidence(value: unknown, field: string): readonly ItemEvidence[] {
  if (Array.isArray(value) && value.length === 0) return [];
  return parseEvidence(value, field);
}

function parseMob(
  value: unknown,
  itemIndex: number,
  category: PrefabCategory,
): MobDetails | null {
  const isMob = category === "mob" || category === "boss";
  if (!isMob) {
    if (value !== null && value !== undefined) {
      throw new Error(`non-Mob item ${itemIndex} mob details must be null`);
    }
    return null;
  }
  if (
    !isRecord(value) ||
    !isRecord(value.appearance) ||
    !Array.isArray(value.appearance.sources) ||
    !Array.isArray(value.appearance.spawnCodes) ||
    !Array.isArray(value.appearance.evidence) ||
    !Array.isArray(value.variants) ||
    !Array.isArray(value.stats) ||
    !Array.isArray(value.mechanics) ||
    !Array.isArray(value.loot)
  ) {
    throw new Error(`Mob item ${itemIndex} details must contain normalized sections`);
  }
  const appearance = value.appearance;
  const appearanceSources = appearance.sources as unknown[];
  const appearanceSpawnCodes = appearance.spawnCodes as unknown[];
  const variants = value.variants.map((raw, variantIndex) => {
    if (!isRecord(raw)) {
      throw new Error(`item ${itemIndex} Mob variant ${variantIndex} is invalid`);
    }
    if (
      raw.role !== "phase" &&
      raw.role !== "variant" &&
      raw.role !== "summon" &&
      raw.role !== "post_defeat"
    ) {
      throw new Error(`item ${itemIndex} Mob variant ${variantIndex} role is invalid`);
    }
    if (typeof raw.order !== "number" || !Number.isInteger(raw.order) || raw.order < 0) {
      throw new Error(`item ${itemIndex} Mob variant ${variantIndex} order is invalid`);
    }
    const role = raw.role as MobVariant["role"];
    return {
      id: requiredString(raw.id, `item ${itemIndex} Mob variant id`),
      prefabId: requiredString(raw.prefabId, `item ${itemIndex} Mob variant prefabId`),
      name: requiredString(raw.name, `item ${itemIndex} Mob variant name`),
      role,
      order: raw.order,
      sprite: parseSprite(raw.sprite, `item ${itemIndex} Mob variant ${variantIndex}`),
    };
  });
  const stats = value.stats.map((raw, statIndex) => {
    if (!isRecord(raw) || (typeof raw.value !== "number" && typeof raw.value !== "string")) {
      throw new Error(`item ${itemIndex} mob stat ${statIndex} is invalid`);
    }
    return {
      key: requiredString(raw.key, `item ${itemIndex} mob stat key`),
      label: requiredString(raw.label, `item ${itemIndex} mob stat label`),
      value: raw.value,
      unit: nullableString(raw.unit, `item ${itemIndex} mob stat unit`),
      sourceVariant: requiredString(
        raw.sourceVariant,
        `item ${itemIndex} mob stat sourceVariant`,
      ),
      evidence: parseMobEvidence(raw.evidence, `item ${itemIndex} mob stat ${statIndex}`),
    };
  });
  const mechanics = value.mechanics.map((raw, mechanicIndex) => {
    if (!isRecord(raw)) {
      throw new Error(`item ${itemIndex} mob mechanic ${mechanicIndex} is invalid`);
    }
    return {
      text: requiredString(raw.text, `item ${itemIndex} mob mechanic text`),
      sourceVariant: requiredString(
        raw.sourceVariant,
        `item ${itemIndex} mob mechanic sourceVariant`,
      ),
      evidence: parseMobEvidence(
        raw.evidence,
        `item ${itemIndex} mob mechanic ${mechanicIndex}`,
      ),
    };
  });
  const loot = value.loot.map((raw, lootIndex) => {
    if (!isRecord(raw)) throw new Error(`item ${itemIndex} mob loot ${lootIndex} is invalid`);
    if (
      typeof raw.minimum !== "number" ||
      !Number.isFinite(raw.minimum) ||
      raw.minimum < 0 ||
      typeof raw.maximum !== "number" ||
      !Number.isFinite(raw.maximum) ||
      raw.maximum < raw.minimum
    ) {
      throw new Error(`item ${itemIndex} mob loot ${lootIndex} quantity is invalid`);
    }
    if (
      raw.method !== "kill" &&
      raw.method !== "mine_post_defeat" &&
      raw.method !== "harvest" &&
      raw.method !== "conditional"
    ) {
      throw new Error(`item ${itemIndex} mob loot ${lootIndex} method is invalid`);
    }
    const method = raw.method as MobRewardMethod;
    return {
      item: parseReference(raw.item, `item ${itemIndex} mob loot ${lootIndex}`),
      minimum: raw.minimum,
      maximum: raw.maximum,
      chance: nullableString(raw.chance, `item ${itemIndex} mob loot chance`),
      method,
      sourceVariant: requiredString(
        raw.sourceVariant,
        `item ${itemIndex} mob loot sourceVariant`,
      ),
      lootTable: nullableString(raw.lootTable, `item ${itemIndex} mob loot lootTable`),
      conditions: nullableString(raw.conditions, `item ${itemIndex} mob loot conditions`),
      evidence: parseMobEvidence(raw.evidence, `item ${itemIndex} mob loot ${lootIndex}`),
    };
  });
  const lootStatus = parseDetailStatus(value.lootStatus, `item ${itemIndex} mob loot`);
  if (lootStatus === "known" && !loot.length) {
    throw new Error(`item ${itemIndex} known mob loot must contain data`);
  }
  return {
    appearance: {
      status: parseDetailStatus(appearance.status, `item ${itemIndex} mob appearance`),
      sources: appearanceSources.map((source, sourceIndex) =>
        requiredString(source, `item ${itemIndex} mob appearance source ${sourceIndex}`),
      ),
      spawnCodes: appearanceSpawnCodes.map((code, codeIndex) =>
        requiredString(code, `item ${itemIndex} mob spawn code ${codeIndex}`),
      ),
      renewable: nullableBoolean(
        appearance.renewable,
        `item ${itemIndex} mob renewable`,
      ),
      respawn: nullableDisplayValue(appearance.respawn, `item ${itemIndex} mob respawn`),
      wikiUrl: nullableString(appearance.wikiUrl, `item ${itemIndex} mob wikiUrl`),
      evidence: parseMobEvidence(appearance.evidence, `item ${itemIndex} mob appearance`),
    },
    variants,
    stats,
    mechanics,
    lootStatus,
    loot,
  };
}

function parseCharacter(value: unknown, itemIndex: number): CharacterProfile | null {
  if (value === null || value === undefined) return null;
  if (!isRecord(value) || !Array.isArray(value.abilities)) {
    throw new Error(`item ${itemIndex} character profile is invalid`);
  }
  return {
    title: nullableString(value.title, `item ${itemIndex} character title`),
    survivability: nullableString(
      value.survivability,
      `item ${itemIndex} character survivability`,
    ),
    quote: nullableString(value.quote, `item ${itemIndex} character quote`),
    abilities: value.abilities.map((raw, abilityIndex) =>
      requiredString(raw, `item ${itemIndex} character ability ${abilityIndex}`),
    ),
  };
}

function nullableBoolean(value: unknown, field: string): boolean | null {
  if (value === null) return null;
  if (typeof value !== "boolean") throw new Error(`${field} must be boolean or null`);
  return value;
}

function nullableDisplayValue(value: unknown, field: string): string | null {
  if (value === null) return null;
  if (typeof value !== "string" && typeof value !== "number") {
    throw new Error(`${field} must be text, number, or null`);
  }
  return String(value);
}

function parseStructureImage(
  value: unknown,
  field: string,
): StructureVisualImage | null {
  if (value === null) return null;
  if (!isRecord(value)) throw new Error(`${field} must be an object or null`);
  const nullableDimension = (dimension: unknown, name: string) => {
    if (dimension === null || dimension === undefined) return null;
    if (typeof dimension !== "number" || !Number.isFinite(dimension) || dimension <= 0) {
      throw new Error(`${field} ${name} is invalid`);
    }
    return dimension;
  };
  return {
    title: nullableString(value.title ?? null, `${field} title`),
    src: requiredString(value.src, `${field} src`),
    mime: nullableString(value.mime ?? null, `${field} mime`),
    width: nullableDimension(value.width, "width"),
    height: nullableDimension(value.height, "height"),
    evidence: parseEvidence(value.evidence, field),
  };
}

function parseStructureDetails(
  value: unknown,
  category: PrefabCategory,
  itemIndex: number,
): StructureDetails | null {
  if (category !== "structure") {
    if (value !== null) {
      throw new Error(`non-structure item ${itemIndex} structureDetails must be null`);
    }
    return null;
  }
  if (!isRecord(value)) {
    throw new Error(`structure item ${itemIndex} structureDetails must be an object`);
  }
  const { origin, construction, functions, craftables, destruction, visual } = value;
  if (
    !isRecord(origin) ||
    !isRecord(construction) ||
    !isRecord(functions) ||
    !isRecord(craftables) ||
    !isRecord(destruction) ||
    !isRecord(visual)
  ) {
    throw new Error(`structure item ${itemIndex} must contain every detail section`);
  }
  if (
    !Array.isArray(origin.sources) ||
    !Array.isArray(construction.ingredients) ||
    !Array.isArray(functions.facts) ||
    !Array.isArray(craftables.recipes) ||
    !Array.isArray(destruction.drops) ||
    !Array.isArray(visual.alternatives)
  ) {
    throw new Error(`structure item ${itemIndex} detail sections must contain arrays`);
  }
  const parseSectionEvidence = (section: Record<string, unknown>, name: string) =>
    parseEvidence(section.evidence, `structure item ${itemIndex} ${name}`);
  const functionFacts = functions.facts.map((raw, factIndex) => {
    if (!isRecord(raw) || !Array.isArray(raw.related)) {
      throw new Error(`structure item ${itemIndex} function ${factIndex} is invalid`);
    }
    return {
      key: requiredString(raw.key, `structure function ${factIndex} key`),
      label: requiredString(raw.label, `structure function ${factIndex} label`),
      value: requiredString(raw.value, `structure function ${factIndex} value`),
      unit: nullableString(raw.unit, `structure function ${factIndex} unit`),
      context: nullableString(raw.context, `structure function ${factIndex} context`),
      related: raw.related.map((entry, index) =>
        requiredString(entry, `structure function ${factIndex} related ${index}`),
      ),
      evidence: parseEvidence(raw.evidence, `structure function ${factIndex}`),
    };
  });
  const stationRecipes = craftables.recipes.map((raw, recipeIndex) => {
    if (!isRecord(raw) || !Array.isArray(raw.ingredients) || !isRecord(raw.restrictions)) {
      throw new Error(`structure station recipe ${recipeIndex} is invalid`);
    }
    return {
      result: parseReference(raw.result, `structure station recipe ${recipeIndex} result`),
      resultAmount: positiveNumber(
        raw.resultAmount,
        `structure station recipe ${recipeIndex} result amount`,
      ),
      ingredients: raw.ingredients.map(parseIngredient),
      station: requiredString(raw.station, `structure station recipe ${recipeIndex} station`),
      tech: nullableString(raw.tech, `structure station recipe ${recipeIndex} tech`),
      restrictions: raw.restrictions,
      note: nullableString(raw.note, `structure station recipe ${recipeIndex} note`),
      evidence: parseEvidence(raw.evidence, `structure station recipe ${recipeIndex}`),
    };
  });
  if (visual.kind !== null && visual.kind !== "inventory_icon" && visual.kind !== "wiki_image") {
    throw new Error(`structure item ${itemIndex} visual kind is invalid`);
  }
  const alternatives = visual.alternatives.map((candidate, candidateIndex) => {
    if (!isRecord(candidate)) {
      throw new Error(`structure visual alternative ${candidateIndex} is invalid`);
    }
    return candidate;
  });
  const outputCount =
    construction.outputCount === null
      ? null
      : positiveNumber(construction.outputCount, `structure item ${itemIndex} outputCount`);
  return {
    origin: {
      status: parseDetailStatus(origin.status, `structure item ${itemIndex} origin`),
      naturallySpawned:
        typeof origin.naturallySpawned === "boolean"
          ? origin.naturallySpawned
          : (() => { throw new Error(`structure item ${itemIndex} naturallySpawned is invalid`); })(),
      renewable: nullableBoolean(origin.renewable, `structure item ${itemIndex} renewable`),
      spawnCode: nullableString(origin.spawnCode, `structure item ${itemIndex} spawnCode`),
      sources: origin.sources.map((entry, index) =>
        requiredString(entry, `structure item ${itemIndex} source ${index}`),
      ),
      respawn: nullableDisplayValue(origin.respawn, `structure item ${itemIndex} respawn`),
      craftable:
        typeof origin.craftable === "boolean"
          ? origin.craftable
          : (() => { throw new Error(`structure item ${itemIndex} craftable is invalid`); })(),
      note: nullableString(origin.note, `structure item ${itemIndex} origin note`),
      evidence: parseSectionEvidence(origin, "origin"),
    },
    construction: {
      status: parseDetailStatus(
        construction.status,
        `structure item ${itemIndex} construction`,
      ),
      outputCount,
      ingredients: construction.ingredients.map(parseIngredient),
      tech: nullableString(construction.tech, `structure item ${itemIndex} tech`),
      station: nullableString(construction.station, `structure item ${itemIndex} station`),
      restrictions: isRecord(construction.restrictions)
        ? construction.restrictions
        : {},
      note: nullableString(construction.note, `structure item ${itemIndex} construction note`),
      evidence: parseSectionEvidence(construction, "construction"),
    },
    functions: {
      status: parseDetailStatus(functions.status, `structure item ${itemIndex} functions`),
      facts: functionFacts,
      reason: nullableString(functions.reason, `structure item ${itemIndex} functions reason`),
      evidence: parseSectionEvidence(functions, "functions"),
    },
    craftables: {
      status: parseDetailStatus(craftables.status, `structure item ${itemIndex} craftables`),
      recipes: stationRecipes,
      reason: nullableString(craftables.reason, `structure item ${itemIndex} craftables reason`),
      evidence: parseSectionEvidence(craftables, "craftables"),
    },
    destruction: {
      status: parseDetailStatus(destruction.status, `structure item ${itemIndex} destruction`),
      destroyable: nullableBoolean(
        destruction.destroyable,
        `structure item ${itemIndex} destroyable`,
      ),
      tool: nullableString(destruction.tool, `structure item ${itemIndex} tool`),
      work: nullableDisplayValue(destruction.work, `structure item ${itemIndex} work`),
      health: nullableDisplayValue(destruction.health, `structure item ${itemIndex} health`),
      burnable: nullableBoolean(destruction.burnable, `structure item ${itemIndex} burnable`),
      drops: destruction.drops,
      regeneration: nullableDisplayValue(
        destruction.regeneration,
        `structure item ${itemIndex} regeneration`,
      ),
      evidence: parseSectionEvidence(destruction, "destruction"),
    },
    visual: {
      status: parseDetailStatus(visual.status, `structure item ${itemIndex} visual`),
      kind: visual.kind,
      sprite: parseSprite(visual.sprite, `structure item ${itemIndex} visual`),
      image: parseStructureImage(visual.image, `structure item ${itemIndex} visual image`),
      alternatives,
      reason: nullableString(visual.reason, `structure item ${itemIndex} visual reason`),
      evidence: parseSectionEvidence(visual, "visual"),
    },
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
  const category = parseCategory(value.category, index);
  return {
    id: requiredString(value.id, `item ${index} id`),
    prefabId: requiredString(value.prefabId, `item ${index} prefabId`),
    namespace,
    category,
    name: requiredString(value.name, `item ${index} name`),
    englishName: nullableString(value.englishName, `item ${index} englishName`),
    description: nullableString(value.description, `item ${index} description`),
    craftingNote: nullableString(value.craftingNote, `item ${index} craftingNote`),
    sprite: parseSprite(value.sprite, `item ${index}`),
    recipe: parseRecipe(value.recipe, index),
    details: parseDetails(value.details, namespace, index),
    mob: parseMob(value.mob, index, category),
    character: parseCharacter(value.character, index),
    structureDetails: parseStructureDetails(value.structureDetails, category, index),
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
    value.schema_version !== 6 ||
    !Array.isArray(value.items)
  ) {
    throw new Error("item payload must use schema version 6 and contain items");
  }
  return curateItems(value.items.map(parseItem));
}
