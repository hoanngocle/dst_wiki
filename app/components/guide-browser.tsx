"use client";

import Image from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";

import { filterGuides, type GuideListEntry } from "@/app/lib/guide-catalog";

const topicLabels: Record<string, string> = {
  "base-building": "Xây căn cứ",
  combat: "Chiến đấu",
  domestication: "Thuần hóa",
  general: "Tổng hợp",
  resources: "Tài nguyên",
};

const audienceLabels: Record<string, string> = {
  beginner: "Cơ bản",
  intermediate: "Trung cấp",
  advanced: "Nâng cao",
};

export function GuideBrowser({ guides }: { guides: readonly GuideListEntry[] }) {
  const [query, setQuery] = useState("");
  const [topic, setTopic] = useState("all");
  const [audience, setAudience] = useState("all");
  const topics = useMemo(
    () => [...new Set(guides.map((guide) => guide.topic))].sort(),
    [guides],
  );
  const audiences = useMemo(
    () => [...new Set(guides.map((guide) => guide.audience))].sort(),
    [guides],
  );
  const visible = useMemo(
    () => filterGuides(guides, query, topic, audience),
    [guides, query, topic, audience],
  );

  function reset() {
    setQuery("");
    setTopic("all");
    setAudience("all");
  }

  return (
    <section aria-labelledby="guide-library" className="mt-10">
      <h2 id="guide-library" className="sr-only">Thư viện hướng dẫn</h2>
      <div className="grid gap-3 rounded-2xl border border-[#c7d2df] bg-[#f8fafc] p-4 shadow-[0_12px_30px_rgba(35,59,88,0.06)] md:grid-cols-[minmax(0,1fr)_14rem_12rem_auto] md:items-end">
        <label className="grid gap-2 text-xs font-semibold uppercase tracking-[0.12em] text-[#607188]">
          Tìm hướng dẫn
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Beefalo, Giant, căn cứ…"
            className="min-h-11 rounded-xl border border-[#c7d2df] bg-white px-3 text-sm font-normal normal-case tracking-normal text-[#172943] outline-none transition focus:border-[#2e5fb3] focus:ring-2 focus:ring-[#2e5fb3]/15"
          />
        </label>
        <label className="grid gap-2 text-xs font-semibold uppercase tracking-[0.12em] text-[#607188]">
          Chủ đề
          <select value={topic} onChange={(event) => setTopic(event.target.value)} className="min-h-11 rounded-xl border border-[#c7d2df] bg-white px-3 text-sm font-normal normal-case tracking-normal text-[#172943]">
            <option value="all">Tất cả chủ đề</option>
            {topics.map((value) => <option key={value} value={value}>{topicLabels[value] ?? value}</option>)}
          </select>
        </label>
        <label className="grid gap-2 text-xs font-semibold uppercase tracking-[0.12em] text-[#607188]">
          Trình độ
          <select value={audience} onChange={(event) => setAudience(event.target.value)} className="min-h-11 rounded-xl border border-[#c7d2df] bg-white px-3 text-sm font-normal normal-case tracking-normal text-[#172943]">
            <option value="all">Mọi trình độ</option>
            {audiences.map((value) => <option key={value} value={value}>{audienceLabels[value] ?? value}</option>)}
          </select>
        </label>
        <button type="button" onClick={reset} aria-label="Đặt lại bộ lọc" className="min-h-11 rounded-xl border border-[#c7d2df] px-4 text-sm font-semibold text-[#2e5fb3] transition hover:border-[#2e5fb3] hover:bg-[#e9eff6]">
          Đặt lại
        </button>
      </div>

      <div className="mt-6 flex items-center justify-between gap-4">
        <p aria-live="polite" className="text-sm font-semibold text-[#53647a]">{visible.length} hướng dẫn</p>
        <p className="hidden text-xs uppercase tracking-[0.14em] text-[#73839a] sm:block">Đọc riêng · Dữ liệu DST</p>
      </div>

      {visible.length ? (
        <div className="mt-4 grid gap-5 md:grid-cols-2">
          {visible.map((guide) => (
            <article key={guide.id} className="group overflow-hidden rounded-2xl border border-[#c7d2df] bg-[#f8fafc] transition duration-200 hover:-translate-y-0.5 hover:border-[#9fb9dc] hover:shadow-[0_18px_40px_rgba(35,59,88,0.10)]">
              <Link href={`/guides/${guide.slug}`} aria-label={`${guide.titleVi} — đọc hướng dẫn`} className="grid h-full sm:grid-cols-[11rem_minmax(0,1fr)]">
                <div className="relative min-h-48 overflow-hidden bg-[#dfe7ef] sm:min-h-full">
                  <Image src={guide.cover.src} alt={guide.cover.alt} width={guide.cover.width} height={guide.cover.height} className="absolute inset-0 h-full w-full object-cover transition duration-300 group-hover:scale-[1.025]" />
                </div>
                <div className="flex min-w-0 flex-col p-5">
                  <div className="flex flex-wrap gap-2 text-[0.68rem] font-semibold uppercase tracking-[0.12em] text-[#2e5fb3]">
                    <span>{topicLabels[guide.topic] ?? guide.topic}</span>
                    <span aria-hidden="true">·</span>
                    <span>{audienceLabels[guide.audience] ?? guide.audience}</span>
                  </div>
                  <h3 className="mt-3 text-xl font-semibold leading-tight tracking-[-0.025em] text-[#172943]">{guide.titleVi}</h3>
                  <p className="mt-1 text-sm text-[#73839a]">{guide.title}</p>
                  <p className="mt-4 line-clamp-3 text-sm leading-6 text-[#53647a]">{guide.summaryVi}</p>
                  <p className="mt-auto pt-5 text-xs font-semibold text-[#607188]">{guide.readingMinutes} phút đọc</p>
                </div>
              </Link>
            </article>
          ))}
        </div>
      ) : (
        <div className="mt-4 rounded-2xl border border-dashed border-[#aebdcd] bg-[#f8fafc] px-6 py-16 text-center">
          <h3 className="text-lg font-semibold text-[#172943]">Không tìm thấy hướng dẫn phù hợp</h3>
          <p className="mt-2 text-sm text-[#607188]">Thử từ khóa rộng hơn hoặc đặt lại bộ lọc.</p>
        </div>
      )}
    </section>
  );
}
