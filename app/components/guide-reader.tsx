import Image from "next/image";
import Link from "next/link";

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
      <header className="border-b border-[#c7d2df] bg-[#e8eef5]">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 py-9 sm:px-6 sm:py-12 lg:grid-cols-[minmax(0,1fr)_minmax(22rem,0.72fr)] lg:items-center lg:px-8">
          <div>
            <Link href="/guides" className="inline-flex min-h-11 items-center text-sm font-semibold text-[#2e5fb3] hover:underline">← Tất cả Guide</Link>
            <p className="mt-4 text-xs font-semibold uppercase tracking-[0.15em] text-[#2e5fb3]">{topicLabels[guide.topic] ?? guide.topic} · {audienceLabels[guide.audience] ?? guide.audience}</p>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-[1.04] tracking-[-0.04em] text-[#14233b] sm:text-5xl">{guide.titleVi}</h1>
            <p className="mt-3 text-lg text-[#607188]">{guide.title}</p>
            <p className="mt-6 max-w-[62ch] text-base leading-7 text-[#43566f]">{guide.summaryVi}</p>
            <div className="mt-6 flex flex-wrap gap-x-5 gap-y-2 text-xs font-semibold text-[#607188]">
              <span>{guide.readingMinutes} phút đọc</span>
              <span>Cập nhật {updated}</span>
              <a href={guide.sourceUrl} target="_blank" rel="noreferrer" className="text-[#2e5fb3] hover:underline">Xem nguồn Fandom ↗</a>
            </div>
          </div>
          <div className="relative aspect-[16/9] overflow-hidden rounded-2xl border border-[#b8c6d5] bg-[#d7dfe8] shadow-[0_18px_45px_rgba(35,59,88,0.12)]">
            <Image src={guide.cover.src} alt={guide.cover.alt} width={guide.cover.width} height={guide.cover.height} priority className="h-full w-full object-cover" />
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-9 sm:px-6 sm:py-12 lg:grid-cols-[15rem_minmax(0,48rem)] lg:justify-center lg:px-8">
        <aside className="lg:sticky lg:top-6 lg:self-start">
          <nav aria-label="Mục lục hướng dẫn" className="rounded-2xl border border-[#c7d2df] bg-[#f8fafc] p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#607188]">Trong bài</p>
            <ol className="mt-3 space-y-1.5">
              {guide.toc.map((row) => (
                <li key={row.id} style={{ paddingLeft: `${Math.max(0, row.level - 2) * 0.75}rem` }}>
                  <a href={`#${row.id}`} className="block rounded-lg px-2 py-1.5 text-sm leading-5 text-[#53647a] hover:bg-[#e9eff6] hover:text-[#2e5fb3]">{row.label}</a>
                </li>
              ))}
            </ol>
          </nav>
        </aside>
        <article className="min-w-0 rounded-2xl border border-[#c7d2df] bg-[#f8fafc] px-5 py-7 shadow-[0_12px_30px_rgba(35,59,88,0.05)] sm:px-8 sm:py-9">
          {guide.sections.map((section) => (
            <section key={section.id} className="wiki-article guide-article" dangerouslySetInnerHTML={{ __html: section.html }} />
          ))}
          <footer className="mt-10 border-t border-[#d7dfe8] pt-6 text-sm leading-6 text-[#607188]">
            Nội dung được chuẩn hóa từ Fandom và chỉ xuất bản khi phù hợp với Don&apos;t Starve Together. <a href={guide.sourceUrl} target="_blank" rel="noreferrer" className="font-semibold text-[#2e5fb3] hover:underline">Xem nguồn Fandom</a>.
          </footer>
        </article>
      </div>
    </main>
  );
}
