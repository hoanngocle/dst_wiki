"use client";

import Image from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";

import { DstField, dstControlClassName } from "@/app/components/dst-field";
import { DstPanel } from "@/app/components/dst-panel";
import {
  filterGuides,
  type GuideCover,
  type GuideListEntry,
} from "@/app/lib/guide-catalog";

export type GuideBrowserEntry = Pick<
  GuideListEntry,
  "id" | "slug" | "titleVi" | "summaryVi" | "topic" | "audience" | "readingMinutes"
> & {
  cover: Pick<GuideCover, "src" | "alt" | "width" | "height">;
};

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

export function GuideBrowser({ guides }: { guides: readonly GuideBrowserEntry[] }) {
  const [query, setQuery] = useState("");
  const [topic, setTopic] = useState("all");
  const [audience, setAudience] = useState("all");
  const topics = useMemo(() => [...new Set(guides.map((guide) => guide.topic))].sort(), [guides]);
  const audiences = useMemo(() => [...new Set(guides.map((guide) => guide.audience))].sort(), [guides]);
  const visible = useMemo(
    () => filterGuides(guides, query, topic, audience),
    [guides, query, topic, audience],
  );

  function reset(): void {
    setQuery("");
    setTopic("all");
    setAudience("all");
  }

  return (
    <section aria-labelledby="guide-library" className="mt-10">
      <h2 id="guide-library" className="sr-only">Thư viện hướng dẫn</h2>
      <DstPanel
        testId="guide-filter-panel"
        className="grid gap-3 p-4 md:grid-cols-[minmax(0,1fr)_14rem_12rem_auto] md:items-end"
      >
        <DstField label="Tìm hướng dẫn" htmlFor="guide-query">
          <input
            id="guide-query"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Beefalo, Giant, căn cứ…"
            className={dstControlClassName}
          />
        </DstField>
        <DstField label="Chủ đề" htmlFor="guide-topic">
          <select
            id="guide-topic"
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
            className={dstControlClassName}
          >
            <option value="all">Tất cả chủ đề</option>
            {topics.map((value) => <option key={value} value={value}>{topicLabels[value] ?? value}</option>)}
          </select>
        </DstField>
        <DstField label="Trình độ" htmlFor="guide-audience">
          <select
            id="guide-audience"
            value={audience}
            onChange={(event) => setAudience(event.target.value)}
            className={dstControlClassName}
          >
            <option value="all">Mọi trình độ</option>
            {audiences.map((value) => <option key={value} value={value}>{audienceLabels[value] ?? value}</option>)}
          </select>
        </DstField>
        <button
          type="button"
          onClick={reset}
          aria-label="Đặt lại bộ lọc"
          className="min-h-11 rounded-xl border border-nova-border bg-nova-surface-soft px-4 text-sm font-semibold text-nova-accent transition hover:border-nova-accent hover:bg-nova-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent"
        >
          Đặt lại
        </button>
      </DstPanel>

      <div className="mt-6 flex items-center justify-between gap-4">
        <p aria-live="polite" className="text-sm font-semibold text-nova-muted">{visible.length} hướng dẫn</p>
        <p className="hidden text-xs tracking-[0.14em] text-nova-faint uppercase sm:block">Đọc riêng · Dữ liệu DST</p>
      </div>

      {visible.length ? (
        <div className="mt-4 grid gap-5 md:grid-cols-2">
          {visible.map((guide) => (
            <article key={guide.id} className="group overflow-hidden rounded-2xl border border-nova-border bg-nova-surface transition duration-200 hover:-translate-y-0.5 hover:border-nova-accent/60 hover:shadow-[0_18px_40px_rgba(0,0,0,0.18)]">
              <Link href={`/guides/${guide.slug}`} aria-label={`${guide.titleVi} — đọc hướng dẫn`} className="grid h-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent focus-visible:ring-inset sm:grid-cols-[11rem_minmax(0,1fr)]">
                <div className="relative min-h-48 overflow-hidden bg-nova-surface-soft sm:min-h-full">
                  <Image src={guide.cover.src} alt={guide.cover.alt} width={guide.cover.width} height={guide.cover.height} className="absolute inset-0 h-full w-full object-cover transition duration-300 group-hover:scale-[1.025]" />
                </div>
                <div className="flex min-w-0 flex-col p-5">
                  <div className="flex flex-wrap gap-2 text-[0.68rem] font-semibold tracking-[0.12em] text-nova-accent uppercase">
                    <span>{topicLabels[guide.topic] ?? guide.topic}</span>
                    <span aria-hidden="true">·</span>
                    <span>{audienceLabels[guide.audience] ?? guide.audience}</span>
                  </div>
                  <h3 className="mt-3 text-xl leading-tight font-semibold tracking-[-0.025em] text-nova-text">{guide.titleVi}</h3>
                  <p className="mt-4 line-clamp-3 text-sm leading-6 text-nova-muted">{guide.summaryVi}</p>
                  <p className="mt-auto pt-5 text-xs font-semibold text-nova-faint">{guide.readingMinutes} phút đọc</p>
                </div>
              </Link>
            </article>
          ))}
        </div>
      ) : (
        <DstPanel className="mt-4 border-dashed px-6 py-16 text-center">
          <h3 className="text-lg font-semibold text-nova-text">Không tìm thấy hướng dẫn phù hợp</h3>
          <p className="mt-2 text-sm text-nova-muted">Thử từ khóa rộng hơn hoặc đặt lại bộ lọc.</p>
        </DstPanel>
      )}
    </section>
  );
}
