import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { GuideReader } from "@/app/components/guide-reader";
import { SiteHeader } from "@/app/components/site-header";
import { findGuide, guideSlugs } from "@/app/lib/guide-content";

export function generateStaticParams(): { slug: string }[] {
  return guideSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const guide = findGuide(slug);
  if (!guide) {
    return {};
  }
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
  const guide = findGuide(slug);
  if (!guide) {
    notFound();
  }

  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader active="guides" />
      <GuideReader guide={guide} />
    </div>
  );
}
