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
  subjectAmount: number;
  ingredients: readonly NormalizedWikiIngredient[];
  station: string | null;
  dlc: string | null;
  character: string | null;
  note: string | null;
};

export type NormalizedWikiSections = {
  subject: NormalizedWikiReference;
  dropTable: { rows: readonly NormalizedWikiDropRow[] };
  usage: { recipes: readonly NormalizedWikiUsageRecipe[] };
};

export type WikiPageDetail = {
  pageId: number;
  title: string;
  canonicalUrl: string;
  html: string;
  summaryViHtml: string | null;
  categories: readonly string[];
  images: readonly WikiDetailImage[];
  revision: {
    id: number;
    sha1: string;
    timestamp: string;
  };
  normalized: NormalizedWikiSections | null;
};

export function buildWikiDetailUrl(page: { pageId: number }): string {
  if (!Number.isInteger(page.pageId) || page.pageId <= 0) {
    throw new Error("Wiki pageId must be a positive integer");
  }

  return `/data/wiki/pages/${page.pageId}.json`;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

const allowedWikiTags = new Set([
  "a", "aside", "b", "blockquote", "br", "code", "dd", "div", "dl", "dt",
  "em", "figcaption", "figure", "h1", "h2", "h3", "h4", "h5", "h6", "hr",
  "i", "img", "li", "ol", "p", "pre", "section", "small", "span", "strong",
  "sub", "sup", "table", "tbody", "td", "th", "thead", "tr", "u", "ul",
]);
const blockedWikiTags = new Set([
  "embed", "iframe", "object", "script", "style", "template",
]);
const blockedWikiClasses = new Set([
  "catlinks", "mw-editsection", "navbox", "navbox-styles", "noexcerpt", "printfooter",
]);
const allowedWikiAttributes = new Set([
  "alt", "class", "colspan", "height", "href", "id", "rowspan", "src", "title", "width",
]);

function validateWikiElement(element: Element, context: string): void {
  const tag = element.localName.toLowerCase();
  if (blockedWikiTags.has(tag) || !allowedWikiTags.has(tag)) {
    throw new Error(`${context} contains a disallowed ${tag} element`);
  }

  const classTokens = element.getAttribute("class")?.split(/\s+/).filter(Boolean) ?? [];
  if (classTokens.some((className) => blockedWikiClasses.has(className))) {
    throw new Error(`${context} contains a blocked Wiki class`);
  }

  for (const attribute of element.getAttributeNames()) {
    const name = attribute.toLowerCase();
    if (name.startsWith("on") || !allowedWikiAttributes.has(name)) {
      throw new Error(`${context} contains a disallowed ${name} attribute`);
    }
    if (name === "href" || name === "src") {
      const value = element.getAttribute(attribute) ?? "";
      let url: URL;
      try {
        url = new URL(value);
      } catch {
        throw new Error(`${context} contains a non-HTTP ${name} URL`);
      }
      if (url.protocol !== "http:" && url.protocol !== "https:") {
        throw new Error(`${context} contains a non-HTTP ${name} URL`);
      }
    }
  }
}

function trustedWikiHtml(value: unknown, context: string): string {
  const html = requiredString(value, context);
  const document = new DOMParser().parseFromString(html, "text/html");
  if (document.head.children.length > 0 || document.body.getAttributeNames().length > 0) {
    throw new Error(`${context} contains markup outside the sanitizer allowlist`);
  }
  for (const element of document.body.querySelectorAll("*")) {
    validateWikiElement(element, context);
  }
  return html;
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
    subjectAmount: positiveNumber(
      value.subjectAmount,
      `normalized Usage recipe ${index} subjectAmount`,
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
    value.schema_version !== 2 ||
    !isRecord(value.subject) ||
    !isRecord(value.dropTable) ||
    !Array.isArray(value.dropTable.rows) ||
    !isRecord(value.usage) ||
    !Array.isArray(value.usage.recipes) ||
    (!value.dropTable.rows.length && !value.usage.recipes.length)
  ) {
    throw new Error("normalized Wiki sections must use schema version 2 and contain data");
  }
  return {
    subject: parseReference(value.subject, "normalized Wiki subject"),
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
    html: trustedWikiHtml(value.html, "wiki detail html"),
    summaryViHtml:
      value.summaryViHtml == null
        ? null
        : trustedWikiHtml(value.summaryViHtml, "wiki detail summaryViHtml"),
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
