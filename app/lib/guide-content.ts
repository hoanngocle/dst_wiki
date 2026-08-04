import {
  parseGuideDetail,
  parseGuideIndex,
  type GuideDetail,
  type GuideIndex,
  type GuideListEntry,
} from "./guide-catalog";
import guideIndexPayload from "@/public/data/guides/index.json";
import giantsPayload from "@/public/data/guides/pages/how-to-kill-the-giants-in-dst.json";
import basePayload from "@/public/data/guides/pages/maximum-efficiency-day-13-base-dst-guide.json";
import slimePayload from "@/public/data/guides/pages/slurtle-slime-guide.json";
import beefaloPayload from "@/public/data/guides/pages/taming-a-beefalo.json";

const index = parseGuideIndex(guideIndexPayload);
const publishedDetails = [
  parseGuideDetail(giantsPayload),
  parseGuideDetail(basePayload),
  parseGuideDetail(slimePayload),
  parseGuideDetail(beefaloPayload),
] as const;

function matchesIndexEntry(detail: GuideDetail, entry: GuideListEntry): boolean {
  return (
    detail.id === entry.id &&
    detail.slug === entry.slug &&
    detail.title === entry.title &&
    detail.titleVi === entry.titleVi &&
    detail.summaryVi === entry.summaryVi &&
    detail.sourceUrl === entry.sourceUrl &&
    detail.cover.src === entry.cover.src &&
    detail.cover.alt === entry.cover.alt &&
    detail.cover.width === entry.cover.width &&
    detail.cover.height === entry.cover.height &&
    detail.cover.sha256 === entry.cover.sha256 &&
    detail.topic === entry.topic &&
    detail.audience === entry.audience &&
    detail.readingMinutes === entry.readingMinutes
  );
}

export function buildGuideRegistry(
  index: GuideIndex,
  details: readonly GuideDetail[],
): readonly GuideDetail[] {
  const detailsBySlug = new Map(details.map((guide) => [guide.slug, guide] as const));
  if (detailsBySlug.size !== index.count) {
    throw new Error("published Guide details must match the reviewed index exactly");
  }

  return index.guides.map((entry) => {
    const detail = detailsBySlug.get(entry.slug);
    if (!detail) {
      throw new Error(`missing published Guide detail: ${entry.slug}`);
    }
    if (!matchesIndexEntry(detail, entry)) {
      throw new Error(`published Guide detail does not match its index entry: ${entry.slug}`);
    }
    return detail;
  });
}

const publishedGuides = buildGuideRegistry(index, publishedDetails);

const guidesBySlug = new Map(publishedGuides.map((guide) => [guide.slug, guide] as const));

export function guideSlugs(): string[] {
  return publishedGuides.map((guide) => guide.slug);
}

export function findGuide(slug: string): GuideDetail | undefined {
  return guidesBySlug.get(slug);
}
