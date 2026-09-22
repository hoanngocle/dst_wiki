"use client";

import { useDeferredValue, useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { DstField, dstControlClassName } from "@/app/components/dst-field";
import { DstPanel } from "@/app/components/dst-panel";
import { SoloLevelingContentCard } from "@/app/components/solo-leveling-content-card";
import { SoloLevelingQuestRow } from "@/app/components/solo-leveling-quest-row";
import { SoloLevelingShopCard } from "@/app/components/solo-leveling-shop-card";
import { filterSoloLeveling, guildQuestDifficulty, visibleSoloLevelingGroups, type SoloLevelingData } from "@/app/lib/solo-leveling";

const PAGE_SIZE = 12;
const ranks = ["E", "D", "C", "B", "A", "S"];
const pageButtonClassName = "min-h-11 cursor-pointer rounded-xl border border-nova-border bg-nova-surface px-4 text-sm font-semibold focus-visible:outline-2 focus-visible:outline-nova-accent disabled:cursor-default disabled:opacity-40";

function subscribeToTopic(onChange: () => void) {
  window.addEventListener("hashchange", onChange);
  window.addEventListener("popstate", onChange);
  return () => {
    window.removeEventListener("hashchange", onChange);
    window.removeEventListener("popstate", onChange);
  };
}

function topicFromHash() {
  return window.location.hash.slice(1);
}

function Pagination({ page, pages, onChange, label }: { page: number; pages: number; onChange: (page: number) => void; label: string }) {
  if (pages <= 1) return null;
  return (
    <nav aria-label={label} className="flex flex-wrap items-center justify-between gap-3">
      <button type="button" className={pageButtonClassName} disabled={page === 1} onClick={() => onChange(page - 1)} aria-label="Trang trước">← Trước</button>
      <span className="text-sm text-nova-muted">Trang {page} / {pages}</span>
      <button type="button" className={pageButtonClassName} disabled={page === pages} onClick={() => onChange(page + 1)} aria-label="Trang sau">Sau →</button>
    </nav>
  );
}

function SoloLevelingTopic({ data, activeGroup, linkedEntryId }: {
  data: SoloLevelingData;
  activeGroup: SoloLevelingData["groups"][number];
  linkedEntryId?: string;
}) {
  const topic = activeGroup.id;
  const [query, setQuery] = useState("");
  const [rank, setRank] = useState("all");
  const [category, setCategory] = useState("all");
  const categories = topic === "daily" || topic === "guild" ? ["Dễ", "Vừa", "Khó"] : [...new Set(activeGroup.entries.map((entry) => entry.category).filter((value): value is string => Boolean(value)))];
  const categoryFilter = topic !== "guild-shop" && categories.length > 1;
  const [page, setPage] = useState(() => Math.floor(Math.max(0, activeGroup.entries.findIndex((entry) => entry.id === linkedEntryId)) / PAGE_SIZE) + 1);
  const resultsRef = useRef<HTMLElement>(null);
  const deferredQuery = useDeferredValue(query);
  const entries = useMemo(() => (filterSoloLeveling(data, deferredQuery, topic)[0]?.entries ?? [])
    .filter((entry) => topic !== "guild-shop" || rank === "all" || entry.shop?.rank === rank)
    .filter((entry) => topic !== "guild" || rank === "all" || entry.rank === rank)
    .filter((entry) => category === "all" || (topic === "guild" ? guildQuestDifficulty(entry.rank) : entry.category) === category), [data, deferredQuery, topic, rank, category]);
  const pages = Math.max(1, Math.ceil(entries.length / PAGE_SIZE));
  const currentPage = Math.min(page, pages);
  const start = (currentPage - 1) * PAGE_SIZE;
  const visibleEntries = entries.slice(start, start + PAGE_SIZE);

  useEffect(() => {
    if (linkedEntryId) document.getElementById(linkedEntryId)?.scrollIntoView?.({ block: "start" });
  }, [linkedEntryId]);

  function clearFilters() {
    setQuery("");
    setRank("all");
    setCategory("all");
    setPage(1);
  }

  function changePage(value: number) {
    setPage(value);
    resultsRef.current?.scrollIntoView?.({ block: "start" });
  }

  return (
    <>
            <DstPanel className={`grid items-end gap-4 p-5 ${topic === "guild" ? "sm:grid-cols-2 xl:grid-cols-[minmax(0,1fr)_9rem_12rem_auto]" : topic === "guild-shop" || categoryFilter ? "sm:grid-cols-[minmax(0,1fr)_12rem_auto]" : "sm:grid-cols-[minmax(0,1fr)_auto]"}`}>
              <DstField label="Tìm trong Solo Leveling" htmlFor="solo-query">
                <input id="solo-query" className={dstControlClassName} type="search" value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} placeholder={`Tìm trong ${activeGroup.title.toLowerCase()}… (hỗ trợ không dấu)`} />
              </DstField>
              {(topic === "guild-shop" || topic === "guild") && <DstField label={topic === "guild" ? "Rank" : "Rank yêu cầu"} htmlFor="solo-rank">
                <select id="solo-rank" className={dstControlClassName} value={rank} onChange={(event) => { setRank(event.target.value); setPage(1); }}>
                  <option value="all">Tất cả Rank</option>
                  {ranks.map((value) => <option key={value} value={value}>Rank {value}</option>)}
                </select>
              </DstField>}
              {categoryFilter && <DstField label={topic === "daily" ? "Độ khó" : topic === "guild" ? "Độ khó (theo Rank)" : "Loại nội dung"} htmlFor="solo-category">
                <select id="solo-category" className={dstControlClassName} value={category} onChange={(event) => { setCategory(event.target.value); setPage(1); }} aria-describedby={topic === "guild" ? "solo-guild-difficulty-note" : undefined}>
                  <option value="all">{topic === "daily" || topic === "guild" ? "Tất cả độ khó" : "Tất cả"}</option>
                  {categories.map((value) => <option key={value} value={value}>{value}</option>)}
                </select>
              </DstField>}
              <button type="button" onClick={clearFilters} className={pageButtonClassName}>Xóa bộ lọc</button>
              {topic === "guild" && <p id="solo-guild-difficulty-note" className="text-xs leading-5 text-nova-faint sm:col-span-full">Nhóm độ khó để tra cứu: Dễ (E–D), Vừa (C–B), Khó (A–S). Đây là cách nhóm theo Rank; mod không khai báo độ khó riêng cho nhiệm vụ Hiệp Hội.</p>}
            </DstPanel>
            <section ref={resultsRef} id={`solo-${topic}`} aria-labelledby={`solo-heading-${topic}`} className="mt-6 scroll-mt-6">
              <div className="mb-5 border-b border-nova-border pb-5">
                <h2 id={`solo-heading-${topic}`} className="text-2xl font-semibold tracking-[-0.03em]">{activeGroup.title}</h2>
                <p className="mt-2 text-sm leading-6 text-nova-muted">{activeGroup.description}</p>
                <p role="status" aria-live="polite" className="mt-3 text-sm text-nova-faint">{entries.length} / {activeGroup.entries.length} mục{entries.length > 0 && ` · Hiển thị ${start + 1}–${start + visibleEntries.length}`}</p>
              </div>
              <div className="mb-5"><Pagination page={currentPage} pages={pages} onChange={changePage} label="Phân trang đầu danh sách" /></div>
              {entries.length === 0 ? <DstPanel className="p-6"><p>Không tìm thấy nội dung phù hợp.</p></DstPanel> : (
                <div className={`grid items-start gap-4 ${["daily", "guild", "exams"].includes(topic) ? "" : ["guild-shop", "dungeon-shop", "items", "effects"].includes(topic) ? "sm:grid-cols-2 xl:grid-cols-3" : "sm:grid-cols-2"}`}>
                  {visibleEntries.map((entry) => topic === "guild" || (topic === "daily" && entry.id !== "daily-rules") || (topic === "exams" && entry.id !== "rank-levels")
                    ? <SoloLevelingQuestRow key={entry.id} entry={entry} topic={topic as "daily" | "guild" | "exams"} />
                    : entry.shop ? <SoloLevelingShopCard key={entry.id} entry={entry} product={entry.shop} /> : <SoloLevelingContentCard key={entry.id} entry={entry} topic={topic} />)}
                </div>
              )}
              <div className="mt-6"><Pagination page={currentPage} pages={pages} onChange={changePage} label="Phân trang cuối danh sách" /></div>
            </section>
    </>
  );
}

export function SoloLevelingBrowser({ data }: { data: SoloLevelingData }) {
  const groups = visibleSoloLevelingGroups(data);
  const hash = useSyncExternalStore(subscribeToTopic, topicFromHash, () => `solo-${groups[0].id}`);
  const requestedTopic = hash.replace(/^solo-/, "");
  const namedTopic = requestedTopic === "items" ? "crafting" : requestedTopic;
  const activeGroup = groups.find((group) => group.id === namedTopic)
    ?? groups.find((group) => group.entries.some((entry) => entry.id === hash))
    ?? groups[0];
  const topic = activeGroup.id;
  const linkedEntryId = activeGroup.entries.some((entry) => entry.id === hash) ? hash : undefined;

  function changeTopic(value: string) {
    window.history.replaceState(null, "", `#solo-${value}`);
    window.dispatchEvent(new Event("hashchange"));
  }

  return (
    <div className="mt-8 grid min-w-0 items-start gap-6 lg:grid-cols-[220px_minmax(0,1fr)]">
      <aside className="rounded-2xl border border-nova-border bg-nova-surface p-3 lg:sticky lg:top-4">
        <p className="px-3 py-2 text-xs font-semibold uppercase tracking-widest text-nova-muted">Mục lục Solo Leveling</p>
        <nav aria-label="Mục lục Solo Leveling" className="flex gap-1 overflow-x-auto lg:flex-col">
          {groups.map((group) => (
            <button
              key={group.id}
              type="button"
              aria-pressed={topic === group.id}
              onClick={() => changeTopic(group.id)}
              className={`flex min-h-11 shrink-0 cursor-pointer items-center justify-between gap-3 rounded-xl px-3 py-2 text-left text-sm font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-nova-accent ${topic === group.id ? "bg-nova-accent text-white" : "text-nova-muted hover:bg-nova-surface-soft"}`}
            >
              <span>{group.title}</span>
              <span className="text-xs opacity-70">{group.entries.length}</span>
            </button>
          ))}
        </nav>
      </aside>
      <div className="min-w-0">
        <SoloLevelingTopic key={linkedEntryId ?? topic} data={data} activeGroup={activeGroup} linkedEntryId={linkedEntryId} />
      </div>
    </div>
  );
}
