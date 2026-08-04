import type { Metadata } from "next";
import Link from "next/link";

import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { DstPanel } from "@/app/components/dst-panel";
import { GuideBrowser, type GuideBrowserEntry } from "@/app/components/guide-browser";
import { SiteHeader } from "@/app/components/site-header";
import { parseGuideIndex } from "@/app/lib/guide-catalog";
import guidePayload from "@/public/data/guides/index.json";

export const metadata: Metadata = {
  title: "Guide DST | Don't Starve Together",
  description: "Thư viện hướng dẫn Don't Starve Together đã chọn lọc và lưu cục bộ.",
};

const index = parseGuideIndex(guidePayload);
const browserGuides: readonly GuideBrowserEntry[] = index.guides.map((guide) => ({
  id: guide.id,
  slug: guide.slug,
  title: guide.title,
  titleVi: guide.titleVi,
  summaryVi: guide.summaryVi,
  cover: {
    src: guide.cover.src,
    alt: guide.cover.alt,
    width: guide.cover.width,
    height: guide.cover.height,
  },
  topic: guide.topic,
  audience: guide.audience,
  readingMinutes: guide.readingMinutes,
}));

export default function GuidesPage() {
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <DstHero
            testId="guide-library-hero"
            eyebrow="Sổ tay DST"
            title="Guide thực chiến, đọc riêng từng bài"
            description="Các bài từ Wiki gốc cùng Guide Tu Tiên chuyên biệt."
            stats={[
              { label: "Bài đã duyệt", value: index.count + 1 },
              { label: "Phạm vi", value: "DST" },
            ]}
            statsAriaLabel="Tổng quan thư viện Guide"
          />
          <DstPanel className="mt-6 overflow-hidden p-5 sm:p-6">
            <Link
              href="/tu-tien"
              className="group flex min-h-11 items-center justify-between gap-4 rounded-xl border border-nova-accent/30 bg-nova-accent/10 p-4 transition hover:border-nova-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent"
            >
              <span>
                <span className="block text-xs font-semibold tracking-[0.14em] text-nova-accent uppercase">Tu Tiên</span>
                <span className="mt-1 block text-lg font-semibold text-nova-text">Cảnh giới Tu Tiên</span>
                <span className="mt-1 block text-sm text-nova-muted">15 lần thăng cấp, đan dược và nguyên liệu tương ứng.</span>
              </span>
              <span aria-hidden="true" className="shrink-0 text-nova-accent transition group-hover:translate-x-1">→</span>
            </Link>
            <GuideBrowser guides={browserGuides} />
          </DstPanel>
        </div>
      </DstPageShell>
    </div>
  );
}
