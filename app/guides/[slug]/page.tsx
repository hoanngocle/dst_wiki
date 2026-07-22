import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { GuideReader } from "@/app/components/guide-reader";
import { SiteHeader } from "@/app/components/site-header";
import { parseGuideDetail, parseGuideIndex } from "@/app/lib/guide-catalog";
import guideIndexPayload from "@/public/data/guides/index.json";
import giantsPayload from "@/public/data/guides/pages/how-to-kill-the-giants-in-dst.json";
import basePayload from "@/public/data/guides/pages/maximum-efficiency-day-13-base-dst-guide.json";
import slimePayload from "@/public/data/guides/pages/slurtle-slime-guide.json";
import beefaloPayload from "@/public/data/guides/pages/taming-a-beefalo.json";

const index = parseGuideIndex(guideIndexPayload);
const details = new Map(
  [giantsPayload, basePayload, slimePayload, beefaloPayload].map((payload) => {
    const guide = parseGuideDetail(payload);
    return [guide.slug, guide] as const;
  }),
);

export function generateStaticParams() {
  return index.guides.map((guide) => ({ slug: guide.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const guide = details.get(slug);
  if (!guide) return {};
  return {
    title: `${guide.titleVi} | Guide DST`,
    description: guide.summaryVi,
    openGraph: {
      title: guide.titleVi,
      description: guide.summaryVi,
      images: [{ url: guide.cover.src, width: guide.cover.width, height: guide.cover.height }],
    },
  };
}

export default async function GuidePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const guide = details.get(slug);
  if (!guide) notFound();

  return (
    <div className="min-h-[100dvh] bg-[#edf1f5] text-[#14233b]">
      <SiteHeader active="guides" />
      <GuideReader guide={guide} />
    </div>
  );
}
