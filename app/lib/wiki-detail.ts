export type WikiDetailImage = {
  title: string;
  src: string;
  mime: string;
  width: number | null;
  height: number | null;
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
  };
}
