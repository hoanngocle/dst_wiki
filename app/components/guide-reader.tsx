import Image from "next/image";
import Link from "next/link";

import { DstHero } from "@/app/components/dst-hero";
import { DstPanel } from "@/app/components/dst-panel";
import type { GuideDetail } from "@/app/lib/guide-catalog";

const topicLabels: Record<string, string> = {
  "base-building": "Xây căn cứ",
  combat: "Chiến đấu",
  domestication: "Thuần hóa",
  resources: "Tài nguyên",
};

const audienceLabels: Record<string, string> = {
  beginner: "Cơ bản",
  intermediate: "Trung cấp",
  advanced: "Nâng cao",
};

export function GuideReader({ guide }: { guide: GuideDetail }) {
  const updated = new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(new Date(guide.revision.timestamp));

  return (
    <main>
      <div className="mx-auto max-w-7xl px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
        <DstHero
          eyebrow={`${topicLabels[guide.topic] ?? guide.topic} · ${audienceLabels[guide.audience] ?? guide.audience}`}
          title={guide.titleVi}
          description={guide.summaryVi}
        >
          <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(20rem,0.72fr)] lg:items-end">
            <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm font-semibold text-nova-muted">
              <Link href="/guides" className="inline-flex min-h-11 items-center rounded-lg text-nova-accent underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent">
                ← Tất cả Guide
              </Link>
              <span>{guide.readingMinutes} phút đọc</span>
              <span>Cập nhật {updated}</span>
              <a href={guide.sourceUrl} target="_blank" rel="noreferrer" className="inline-flex min-h-11 items-center rounded-lg text-nova-accent underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent">
                Xem nguồn Fandom ↗
              </a>
            </div>
            <div className="relative aspect-[16/9] overflow-hidden rounded-2xl border border-nova-border bg-nova-surface-soft shadow-[0_18px_45px_rgba(0,0,0,0.2)]">
              <Image src={guide.cover.src} alt={guide.cover.alt} width={guide.cover.width} height={guide.cover.height} priority className="h-full w-full object-cover" />
            </div>
          </div>
        </DstHero>
      </div>

      <div className={`mx-auto grid max-w-7xl gap-8 px-4 pb-9 sm:px-6 sm:pb-12 lg:justify-center lg:px-8 ${guide.toc.length ? "lg:grid-cols-[15rem_minmax(0,48rem)]" : "lg:grid-cols-[minmax(0,48rem)]"}`}>
        {guide.toc.length ? (
          <aside className="lg:sticky lg:top-6 lg:self-start">
            <DstPanel className="p-4">
              <nav aria-label="Mục lục hướng dẫn">
                <p className="text-xs font-semibold tracking-[0.14em] text-nova-faint uppercase">Trong bài</p>
                <ol className="mt-3 space-y-1.5">
                  {guide.toc.map((row) => (
                    <li key={row.id} style={{ paddingLeft: `${Math.max(0, row.level - 2) * 0.75}rem` }}>
                      <a href={`#${row.id}`} className="flex min-h-11 items-center rounded-lg px-2 py-1.5 text-sm leading-5 text-nova-muted transition hover:bg-nova-surface-soft hover:text-nova-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent">{row.label}</a>
                    </li>
                  ))}
                </ol>
              </nav>
            </DstPanel>
          </aside>
        ) : null}
        <DstPanel testId="guide-article" className="min-w-0 px-5 py-7 sm:px-8 sm:py-9">
          <article>
            {guide.sections.map((section) => (
              <section key={section.id} className="wiki-article guide-article" dangerouslySetInnerHTML={{ __html: section.html }} />
            ))}
            <footer className="mt-10 border-t border-nova-border pt-6 text-sm leading-6 text-nova-muted">
              Nội dung được chuẩn hóa từ Fandom và chỉ xuất bản khi phù hợp với Don&apos;t Starve Together. <a href={guide.sourceUrl} target="_blank" rel="noreferrer" className="inline-flex min-h-11 items-center rounded-lg font-semibold text-nova-accent underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent">Xem nguồn Fandom</a>.
            </footer>
          </article>
        </DstPanel>
      </div>
    </main>
  );
}
