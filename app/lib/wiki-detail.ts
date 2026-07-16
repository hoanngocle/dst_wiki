export type WikiDetailImage = {
  title: string;
  src: string;
  mime: string;
  width: number | null;
  height: number | null;
};

export type NormalizedWikiReference = {
  title: string;
  url: string;
  entityId: string | null;
  iconUrl?: string | null;
};

export type NormalizedWikiDropRow = {
  sources: readonly NormalizedWikiReference[];
  quantity: string;
  chance: string;
  context: string | null;
};

export type NormalizedWikiIngredient = {
  item: NormalizedWikiReference;
  amount: number;
};

export type NormalizedWikiUsageRecipe = {
  result: NormalizedWikiReference;
  resultAmount: number;
  nightmareFuelAmount: number;
  ingredients: readonly NormalizedWikiIngredient[];
  station: string | null;
  dlc: string | null;
  character: string | null;
  note: string | null;
};

export type NormalizedWikiSections = {
  dropTable: { rows: readonly NormalizedWikiDropRow[] };
  usage: { recipes: readonly NormalizedWikiUsageRecipe[] };
};

export type WikiPageDetail = {
  pageId: number;
  title: string;
  canonicalUrl: string;
  html: string;
  categories: readonly string[];
  images: readonly WikiDetailImage[];
  revision: {
    id: number;
    sha1: string;
    timestamp: string;
  };
  normalized: NormalizedWikiSections | null;
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

function nullableString(value: unknown, field: string): string | null {
  if (value === null) return null;
  return requiredString(value, field);
}

function nullableDimension(value: unknown, field: string): number | null {
  if (value === null) return null;
  return positiveInteger(value, field);
}

function parseImage(value: unknown, index: number): WikiDetailImage {
  if (!isRecord(value)) {
    throw new Error(`wiki detail image ${index} must be an object`);
  }
  return {
    title: requiredString(value.title, `wiki detail image ${index} title`),
    src: requiredString(value.src, `wiki detail image ${index} src`),
    mime: requiredString(value.mime, `wiki detail image ${index} mime`),
    width: nullableDimension(value.width, `wiki detail image ${index} width`),
    height: nullableDimension(value.height, `wiki detail image ${index} height`),
  };
}

function parseReference(value: unknown, field: string): NormalizedWikiReference {
  if (!isRecord(value)) {
    throw new Error(`${field} must be an object`);
  }
  return {
    title: requiredString(value.title, `${field} title`),
    url: requiredString(value.url, `${field} url`),
    entityId: nullableString(value.entityId, `${field} entityId`),
    iconUrl:
      value.iconUrl == null ? null : requiredString(value.iconUrl, `${field} iconUrl`),
  };
}

function parseDropRow(value: unknown, index: number): NormalizedWikiDropRow {
  if (!isRecord(value) || !Array.isArray(value.sources) || !value.sources.length) {
    throw new Error(`normalized Drop row ${index} must contain sources`);
  }
  return {
    sources: value.sources.map((source, sourceIndex) =>
      parseReference(source, `normalized Drop row ${index} source ${sourceIndex}`),
    ),
    quantity: requiredString(value.quantity, `normalized Drop row ${index} quantity`),
    chance: requiredString(value.chance, `normalized Drop row ${index} chance`),
    context: nullableString(value.context, `normalized Drop row ${index} context`),
  };
}

function parseUsageRecipe(
  value: unknown,
  index: number,
): NormalizedWikiUsageRecipe {
  if (!isRecord(value) || !Array.isArray(value.ingredients)) {
    throw new Error(`normalized Usage recipe ${index} must be an object`);
  }
  return {
    result: parseReference(value.result, `normalized Usage recipe ${index} result`),
    resultAmount: positiveNumber(
      value.resultAmount,
      `normalized Usage recipe ${index} resultAmount`,
    ),
    nightmareFuelAmount: positiveNumber(
      value.nightmareFuelAmount,
      `normalized Usage recipe ${index} nightmareFuelAmount`,
    ),
    ingredients: value.ingredients.map((ingredient, ingredientIndex) => {
      if (!isRecord(ingredient)) {
        throw new Error(
          `normalized Usage recipe ${index} ingredient ${ingredientIndex} must be an object`,
        );
      }
      return {
        item: parseReference(
          ingredient.item,
          `normalized Usage recipe ${index} ingredient ${ingredientIndex}`,
        ),
        amount: positiveNumber(
          ingredient.amount,
          `normalized Usage recipe ${index} ingredient ${ingredientIndex} amount`,
        ),
      };
    }),
    station: nullableString(value.station, `normalized Usage recipe ${index} station`),
    dlc: nullableString(value.dlc, `normalized Usage recipe ${index} dlc`),
    character: nullableString(
      value.character,
      `normalized Usage recipe ${index} character`,
    ),
    note: nullableString(value.note, `normalized Usage recipe ${index} note`),
  };
}

function parseNormalizedSections(value: unknown): NormalizedWikiSections | null {
  if (value === undefined) return null;
  if (
    !isRecord(value) ||
    value.schema_version !== 1 ||
    !isRecord(value.dropTable) ||
    !Array.isArray(value.dropTable.rows) ||
    !value.dropTable.rows.length ||
    !isRecord(value.usage) ||
    !Array.isArray(value.usage.recipes) ||
    !value.usage.recipes.length
  ) {
    throw new Error("normalized Wiki sections must use schema version 1 and contain rows");
  }
  return {
    dropTable: { rows: value.dropTable.rows.map(parseDropRow) },
    usage: { recipes: value.usage.recipes.map(parseUsageRecipe) },
  };
}

export function parseWikiPageDetail(value: unknown): WikiPageDetail {
  if (
    !isRecord(value) ||
    value.schema_version !== 1 ||
    !Array.isArray(value.categories) ||
    !Array.isArray(value.images) ||
    !isRecord(value.revision)
  ) {
    throw new Error("wiki detail must use schema version 1 and contain arrays");
  }

  return {
    pageId: positiveInteger(value.pageId, "wiki detail pageId"),
    title: requiredString(value.title, "wiki detail title"),
    canonicalUrl: requiredString(value.canonicalUrl, "wiki detail canonicalUrl"),
    html: requiredString(value.html, "wiki detail html"),
    categories: value.categories.map((category, index) =>
      requiredString(category, `wiki detail category ${index}`),
    ),
    images: value.images.map(parseImage),
    revision: {
      id: positiveInteger(value.revision.id, "wiki detail revision id"),
      sha1: requiredString(value.revision.sha1, "wiki detail revision sha1"),
      timestamp: requiredString(
        value.revision.timestamp,
        "wiki detail revision timestamp",
      ),
    },
    normalized: parseNormalizedSections(value.normalized),
  };
}
