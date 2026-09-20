"use client";

/* eslint-disable @next/next/no-img-element -- Locally mirrored game sprites and detail illustrations have heterogeneous dimensions. */
import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "./ui/dialog";
import { lingGioiImage, searchVietnamese, type LingGioiItem, type LingGioiSection } from "@/app/lib/ling-gioi";

function subscribe(listener: () => void) {
  window.addEventListener("hashchange", listener);
  window.addEventListener("popstate", listener);
  return () => { window.removeEventListener("hashchange", listener); window.removeEventListener("popstate", listener); };
}
const snapshot = () => window.location.hash;
const serverSnapshot = () => "";
function navigate(values: Record<string, string>) {
  const params = new URLSearchParams(window.location.hash.slice(1));
  for (const [key, value] of Object.entries(values)) {
    if (value) params.set(key, value); else params.delete(key);
  }
  window.history.pushState(null, "", `${window.location.pathname}${window.location.search}#${params}`);
  window.dispatchEvent(new Event("hashchange"));
}

function RichText({ text, items }: { text: string; items: LingGioiItem[] }) {
  const references = new Map(items.map(item => [item.name.replace(/\s*\([^)]*\)/g, "").trim().toLocaleLowerCase("vi"), item]));
  const terms = [...references.keys()].filter(name => name.length >= 5).sort((a, b) => b.length - a.length).map(name => name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const referencePattern = terms.length ? new RegExp(`(?<![\\p{L}\\p{N}])(${terms.join("|")})(?![\\p{L}\\p{N}])`, "giu") : null;
  const parts = text.split(/(\[\[(?:图片|image):[^\]]+\]\]|\[\[[^\]]+\]\]|\[images\/[^\]]+\])/g);
  return <>{parts.map((part, i) => {
    const figure = part.match(/^\[\[(?:图片|image):([^|\]]+)(?:\|([^\]]*))?\]\]$/);
    if (figure) {
      const src = lingGioiImage(figure[1]);
      return src ? <span key={i} className="my-4 block rounded-xl border border-nova-border bg-nova-surface-soft p-3"><img src={src} alt={figure[2] || "Hình minh họa"} loading="lazy" className="mx-auto max-h-96 max-w-full object-contain" />{figure[2] && <span className="mt-2 block text-center text-xs text-nova-muted">{figure[2]}</span>}</span> : null;
    }
    if (/^\[images\//.test(part)) {
      const src = lingGioiImage(part.slice(1, -1));
      return src ? <img key={i} src={src} alt="" loading="lazy" width={28} height={28} className="mx-1 inline-block h-7 w-7 object-contain align-middle" /> : null;
    }
    const ref = part.match(/^\[\[([^\]]+)\]\]$/);
    if (ref) {
      const item = items.find(item => [item.id, item.name, item.originalName].includes(ref[1]));
      return item ? <button key={i} className="text-nova-accent underline underline-offset-2" onClick={() => navigate({ item: item.id, sec: item.section })}>{item.name}</button> : <span key={i}>{ref[1]}</span>;
    }
    return <span key={i}>{referencePattern ? part.split(referencePattern).map((fragment, j) => {
      const target = references.get(fragment.toLocaleLowerCase("vi"));
      return target ? <button key={j} className="text-nova-accent underline underline-offset-2" onClick={() => navigate({ item: target.id, sec: target.section })}>{fragment}</button> : fragment;
    }) : part}</span>;
  })}</>;
}

export function LingGioiBrowser({ sections, items }: { sections: LingGioiSection[]; items: LingGioiItem[] }) {
  const hash = useSyncExternalStore(subscribe, snapshot, serverSnapshot);
  const params = new URLSearchParams(hash.slice(1));
  const section = params.get("sec") || "";
  const selected = items.find(item => item.id === params.get("item"));
  const opener = useRef<HTMLButtonElement | null>(null);
  const searchInput = useRef<HTMLInputElement | null>(null);
  const dialogContent = useRef<HTMLDivElement | null>(null);
  const dialogTitle = useRef<HTMLHeadingElement | null>(null);
  const selectedId = selected?.id;
  useEffect(() => {
    if (dialogContent.current) dialogContent.current.scrollTop = 0;
    dialogTitle.current?.focus();
  }, [selectedId]);
  const [query, setQuery] = useState("");
  const normalizedQuery = searchVietnamese(query.trim());
  const results = items.filter(item => (!section || item.section === section) && searchVietnamese([item.name, item.summary, item.details, item.recipe, ...item.tags, item.id].join(" ")).includes(normalizedQuery));
  const sectionName = sections.find(s => s.id === section)?.name || "Tất cả nội dung";
  return <div className="mt-8 grid items-start gap-6 lg:grid-cols-[220px_minmax(0,1fr)]">
    <aside className="rounded-2xl border border-nova-border bg-nova-surface p-3 lg:sticky lg:top-4">
      <p className="px-3 py-2 text-xs font-semibold uppercase tracking-widest text-nova-muted">Mục lục Linh Giới</p>
      <nav aria-label="Mục lục Linh Giới" className="flex gap-1 overflow-x-auto lg:flex-col">
        {[{ id: "", name: "Tất cả nội dung" }, ...sections].map(s => <button key={s.id} aria-pressed={section === s.id} onClick={() => { setQuery(""); navigate({ sec: s.id, item: "" }); }} className={`flex min-h-11 shrink-0 items-center justify-between gap-3 rounded-xl px-3 py-2 text-left text-sm ${section === s.id ? "bg-nova-accent text-white" : "text-nova-muted hover:bg-nova-surface-soft"}`}><span>{s.name}</span><span className="text-xs opacity-70">{items.filter(item => !s.id || item.section === s.id).length}</span></button>)}
      </nav>
    </aside>
    <div className="min-w-0">
      <label htmlFor="ling-gioi-search" className="mb-2 block text-sm font-semibold">Tìm trong Linh Giới</label>
      <input ref={searchInput} id="ling-gioi-search" type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder="Tên, công thức, tác dụng… có thể gõ không dấu" className="min-h-12 w-full rounded-xl border border-nova-border bg-nova-surface px-4 text-nova-text outline-none focus:ring-2 focus:ring-nova-accent" />
      <div className="my-5 flex items-baseline justify-between gap-3"><h2 className="text-xl font-semibold">{sectionName}</h2><span role="status" className="text-sm text-nova-muted">{results.length} mục</span></div>
      {results.length ? <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{results.map(item => <button key={item.id} onClick={event => { opener.current = event.currentTarget; navigate({ item: item.id }); }} className="group flex h-full flex-col rounded-2xl border border-nova-border bg-nova-surface p-5 text-left transition-colors hover:border-nova-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent">
        <div className="mb-4 flex w-full items-center gap-3">{lingGioiImage(item.image) ? <img src={lingGioiImage(item.image)} alt="" width={56} height={56} loading="lazy" className="h-14 w-14 shrink-0 object-contain" /> : <span aria-hidden="true" className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-nova-surface-soft text-xl text-nova-accent">◇</span>}<h3 className="font-semibold leading-6">{item.name}</h3></div>
        {item.hidden && <span className="mb-2 text-xs text-nova-accent">Nguồn đánh dấu chưa triển khai</span>}
        <p className="text-sm leading-6 text-nova-muted">{item.summary}</p><span className="mt-auto pt-4 text-xs font-semibold text-nova-accent">Xem chi tiết →</span>
      </button>)}</div> : <div className="rounded-2xl border border-nova-border bg-nova-surface p-8 text-center text-nova-muted"><p>{query ? "Không tìm thấy mục phù hợp." : "Trang nguồn chưa có nội dung trong mục này."}</p>{query && <button className="mt-3 text-nova-accent underline" onClick={() => setQuery("")}>Xóa tìm kiếm</button>}</div>}
    </div>
    <Dialog open={Boolean(selected)} onOpenChange={open => { if (!open) navigate({ item: "" }); }}>
      {selected && <DialogContent ref={dialogContent} onOpenAutoFocus={event => { event.preventDefault(); dialogTitle.current?.focus(); }} onCloseAutoFocus={event => { event.preventDefault(); (opener.current?.isConnected ? opener.current : searchInput.current)?.focus(); }} className="max-h-[90dvh] overflow-y-auto border-nova-border bg-nova-surface text-nova-text sm:max-w-3xl sm:p-8">
        <DialogTitle ref={dialogTitle} tabIndex={-1} className="pr-5 text-2xl leading-8 outline-none">{selected.name}</DialogTitle>
        <DialogDescription className="leading-6">{selected.summary}</DialogDescription>
        {selected.hidden && <p className="rounded-lg bg-nova-surface-soft p-3 text-sm">Mục này được nguồn đánh dấu chưa triển khai.</p>}
        {selected.recipe && <section className="rounded-xl border border-nova-border bg-nova-surface-soft p-4"><h3 className="mb-2 font-semibold">Công thức chế tạo</h3><div className="whitespace-pre-wrap text-sm leading-7"><RichText text={selected.recipe} items={items} /></div></section>}
        <article className="space-y-4">{selected.details.split(/\n\s*\n/).map((paragraph, i) => <div key={i} className="whitespace-pre-wrap break-words text-sm leading-7"><RichText text={paragraph} items={items} /></div>)}</article>
        <a href={`https://eyanhuahu.github.io/lingjie/#item=${encodeURIComponent(selected.id)}`} target="_blank" rel="noreferrer" className="border-t border-nova-border pt-4 text-sm text-nova-accent underline">Đối chiếu bài gốc ↗</a>
      </DialogContent>}
    </Dialog>
  </div>;
}
