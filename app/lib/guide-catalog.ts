export type GuideCover = {
  src: string;
  alt: string;
  width: number;
  height: number;
  sha256: string;
};

export type GuideListEntry = {
  id: string;
  slug: string;
  title: string;
  titleVi: string;
  summaryVi: string;
  sourceUrl: string;
  cover: GuideCover;
  topic: string;
  audience: string;
  readingMinutes: number;
};

export type GuideIndex = {
  schemaVersion: 1;
  count: number;
  guides: readonly GuideListEntry[];
};

export type GuideTocEntry = { id: string; label: string; level: number };
export type GuideSection = { id: string; heading: string; level: number; html: string };

export type GuideDetail = GuideListEntry & {
  schemaVersion: 1;
  revision: { id: number; timestamp: string; sha1: string };
  toc: readonly GuideTocEntry[];
  sections: readonly GuideSection[];
};

function record(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`${label} must be an object`);
  }
  return value as Record<string, unknown>;
}

function text(value: unknown, label: string): string {
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`${label} must be a non-empty string`);
  }
  return value.trim();
}

function integer(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isInteger(value) || value <= 0) {
    throw new Error(`${label} must be a positive integer`);
  }
  return value;
}

function parseCover(value: unknown): GuideCover {
  const cover = record(value, "guide cover");
  const src = text(cover.src, "guide cover src");
  if (!src.startsWith("/assets/guides/")) {
    throw new Error("guide cover src must be a local Guide asset");
  }
  return {
    src,
    alt: text(cover.alt, "guide cover alt"),
    width: integer(cover.width, "guide cover width"),
    height: integer(cover.height, "guide cover height"),
    sha256: text(cover.sha256, "guide cover sha256"),
  };
}

function parseEntry(value: unknown): GuideListEntry {
  const guide = record(value, "guide");
  const slug = text(guide.slug, "guide slug");
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
    throw new Error("guide slug must be URL-safe");
  }
  const sourceUrl = text(guide.sourceUrl, "guide sourceUrl");
  if (!sourceUrl.startsWith("https://dontstarve.fandom.com/wiki/")) {
    throw new Error("guide sourceUrl must use the reviewed Fandom source");
  }
  return {
    id: text(guide.id, "guide id"),
    slug,
    title: text(guide.title, "guide title"),
    titleVi: text(guide.titleVi, "guide titleVi"),
    summaryVi: text(guide.summaryVi, "guide summaryVi"),
    sourceUrl,
    cover: parseCover(guide.cover),
    topic: text(guide.topic, "guide topic"),
    audience: text(guide.audience, "guide audience"),
    readingMinutes: integer(guide.readingMinutes, "guide readingMinutes"),
  };
}

export function parseGuideIndex(value: unknown): GuideIndex {
  const payload = record(value, "guide index");
  if (payload.schemaVersion !== 1 || !Array.isArray(payload.guides)) {
    throw new Error("guide index must use schema version 1 and contain guides");
  }
  const guides = payload.guides.map(parseEntry);
  const count = integer(payload.count, "guide index count");
  if (count !== guides.length) {
    throw new Error("guide index count does not match guides");
  }
  const ids = new Set<string>();
  const slugs = new Set<string>();
  for (const guide of guides) {
    if (ids.has(guide.id)) throw new Error(`duplicate guide id: ${guide.id}`);
    if (slugs.has(guide.slug)) throw new Error(`duplicate guide slug: ${guide.slug}`);
    ids.add(guide.id);
    slugs.add(guide.slug);
  }
  return { schemaVersion: 1, count, guides };
}

export function parseGuideDetail(value: unknown): GuideDetail {
  const payload = record(value, "guide detail");
  if (
    payload.schemaVersion !== 1 ||
    !Array.isArray(payload.toc) ||
    !Array.isArray(payload.sections)
  ) {
    throw new Error("guide detail must use schema version 1 and contain toc and sections");
  }
  const entry = parseEntry(payload);
  const revision = record(payload.revision, "guide revision");
  const rawToc = payload.toc.map((value, index) => {
    const row = record(value, `guide toc ${index}`);
    return {
      id: text(row.id, `guide toc ${index} id`),
      label: text(row.label, `guide toc ${index} label`),
      level: integer(row.level, `guide toc ${index} level`),
    };
  });
  const anchors = new Set<string>();
  for (const row of rawToc) {
    if (anchors.has(row.id)) throw new Error(`duplicate guide anchor: ${row.id}`);
    anchors.add(row.id);
  }
  const sections = payload.sections.map((value, index) => {
    const row = record(value, `guide section ${index}`);
    return {
      id: text(row.id, `guide section ${index} id`),
      heading: text(row.heading, `guide section ${index} heading`),
      level: integer(row.level, `guide section ${index} level`),
      html: text(row.html, `guide section ${index} html`),
    };
  });
  if (!sections.length) throw new Error("guide detail sections must not be empty");
  const sectionAnchors = new Set(sections.map((section) => section.id));
  for (const section of sections) {
    for (const match of section.html.matchAll(/\bid=(?:"([^"]+)"|'([^']+)')/g)) {
      const anchor = match[1] ?? match[2];
      if (anchor) sectionAnchors.add(anchor);
    }
  }
  const toc = rawToc
    .filter((row) => row.label.toLocaleLowerCase("en") !== "contents")
    .filter((row) => sectionAnchors.has(row.id))
    .map((row) => ({ ...row, label: row.label.replace(/\[\]\s*$/, "").trim() }));
  return {
    ...entry,
    schemaVersion: 1,
    revision: {
      id: integer(revision.id, "guide revision id"),
      timestamp: text(revision.timestamp, "guide revision timestamp"),
      sha1: text(revision.sha1, "guide revision sha1"),
    },
    toc,
    sections,
  };
}

function searchable(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .toLocaleLowerCase("vi");
}

export function filterGuides(
  guides: readonly GuideListEntry[],
  query: string,
  topic: string,
  audience: string,
): readonly GuideListEntry[] {
  const needle = searchable(query.trim());
  return guides.filter((guide) => {
    const haystack = searchable(
      `${guide.titleVi} ${guide.title} ${guide.summaryVi}`,
    );
    return (
      (!needle || haystack.includes(needle)) &&
      (topic === "all" || guide.topic === topic) &&
      (audience === "all" || guide.audience === audience)
    );
  });
}
