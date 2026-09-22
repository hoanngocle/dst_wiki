"use client";

import { MagnifyingGlass, Sparkle } from "@phosphor-icons/react";
import { useMemo, useState } from "react";

import { DstField, dstControlClassName } from "@/app/components/dst-field";
import { DstPanel } from "@/app/components/dst-panel";
import { GameSprite } from "@/app/components/game-sprite";
import type { SpriteDescriptor } from "@/app/lib/item-catalog";
import {
  filterPhamNhanAffixes,
  type AffixFilter,
  type AffixRarity,
  type PhamNhanAffix,
} from "@/app/lib/pham-nhan-affixes";

const rarityMeta: Record<AffixRarity, { label: string; frame: string; badge: string }> = {
  common: {
    label: "Thường",
    frame: "border-slate-500/55 bg-slate-500/10",
    badge: "border-slate-400/30 bg-slate-400/10 text-slate-200",
  },
  rare: {
    label: "Hiếm",
    frame: "border-amber-500/60 bg-amber-500/10",
    badge: "border-amber-400/35 bg-amber-400/10 text-amber-200",
  },
  "super-rare": {
    label: "Cực hiếm",
    frame: "border-rose-500/65 bg-rose-500/10",
    badge: "border-rose-400/35 bg-rose-400/10 text-rose-200",
  },
};

const filters: { id: AffixFilter; label: string }[] = [
  { id: "all", label: "Tất cả" },
  { id: "common", label: "Thường" },
  { id: "rare", label: "Hiếm" },
  { id: "super-rare", label: "Cực hiếm" },
];

function AffixCard({ affix, stoneSprite }: { affix: PhamNhanAffix; stoneSprite: SpriteDescriptor | null }) {
  const meta = rarityMeta[affix.rarity];

  return (
    <article className={`rounded-2xl border p-4 transition-colors hover:border-nova-accent/60 ${meta.frame}`}>
      <div className="flex items-start gap-4">
        <div className={`grid h-16 w-16 shrink-0 place-items-center rounded-xl border-2 ${meta.frame}`}>
          <GameSprite sprite={stoneSprite} size={50} label="Đá Thuộc Tính" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-[0.12em] ${meta.badge}`}>
              {meta.label}
            </span>
            <code className="break-all text-xs text-nova-faint">{affix.id}</code>
          </div>
          <h3 className="text-lg font-semibold leading-tight text-nova-text">{affix.name}</h3>
        </div>
      </div>
      <p className="mt-4 text-sm leading-6 text-nova-text">{affix.description}</p>
      {affix.details.length > 0 ? (
        <ul className="mt-3 space-y-1.5 border-t border-nova-border/70 pt-3 text-sm leading-5 text-nova-muted">
          {affix.details.map((detail) => (
            <li key={detail} className="flex gap-2">
              <span aria-hidden="true" className="mt-[0.45rem] h-1.5 w-1.5 shrink-0 rounded-full bg-nova-accent" />
              <span>{detail}</span>
            </li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}

export function PhamNhanAffixBrowser({ affixes, stoneSprite }: { affixes: PhamNhanAffix[]; stoneSprite: SpriteDescriptor | null }) {
  const [query, setQuery] = useState("");
  const [rarity, setRarity] = useState<AffixFilter>("all");
  const visible = useMemo(() => filterPhamNhanAffixes(affixes, query, rarity), [affixes, query, rarity]);
  const counts = useMemo(() => ({
    all: affixes.length,
    common: affixes.filter((affix) => affix.rarity === "common").length,
    rare: affixes.filter((affix) => affix.rarity === "rare").length,
    "super-rare": affixes.filter((affix) => affix.rarity === "super-rare").length,
  }), [affixes]);

  return (
    <section id="da-thuoc-tinh" aria-labelledby="affix-title" className="mb-8 scroll-mt-24">
      <DstPanel className="overflow-hidden">
        <div className="border-b border-nova-border bg-[radial-gradient(circle_at_top_right,rgba(180,103,255,0.13),transparent_42%)] p-5 sm:p-6">
          <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
            <div className="max-w-3xl">
              <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-nova-accent">
                <Sparkle aria-hidden="true" size={16} weight="fill" />
                Hệ thống cường hóa
              </div>
              <h2 id="affix-title" className="text-2xl font-bold tracking-tight text-nova-text sm:text-3xl">Đá Thuộc Tính · Affix</h2>
              <p className="mt-2 text-sm leading-6 text-nova-muted">
                Toàn bộ thuộc tính có thể xuất hiện trên trang bị. Các Affix hiện dùng chung icon Đá Thuộc Tính; màu khung thể hiện độ hiếm.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center text-xs sm:min-w-72">
              {(["common", "rare", "super-rare"] as const).map((key) => (
                <div key={key} className={`rounded-xl border px-2 py-2 ${rarityMeta[key].frame}`}>
                  <strong className="block text-lg text-nova-text">{counts[key]}</strong>
                  <span className="text-nova-muted">{rarityMeta[key].label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="p-5 sm:p-6">
          <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
            <DstField label="Tìm Affix" htmlFor="affix-search">
              <div className="relative">
                <MagnifyingGlass aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-nova-faint" size={18} />
                <input
                  id="affix-search"
                  type="search"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Tên, ID, tác dụng hoặc loại trang bị..."
                  className={`${dstControlClassName} pl-10`}
                />
              </div>
            </DstField>
            <div aria-label="Lọc Affix theo độ hiếm" className="flex flex-wrap gap-2">
              {filters.map((filter) => (
                <button
                  key={filter.id}
                  type="button"
                  aria-pressed={rarity === filter.id}
                  onClick={() => setRarity(filter.id)}
                  className={`min-h-11 rounded-xl border px-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent/60 ${
                    rarity === filter.id
                      ? "border-nova-accent bg-nova-accent text-slate-950"
                      : "border-nova-border bg-nova-surface-soft text-nova-muted hover:border-nova-accent/60 hover:text-nova-text"
                  }`}
                >
                  {filter.label} <span className="opacity-75">{counts[filter.id]}</span>
                </button>
              ))}
            </div>
          </div>

          <p aria-live="polite" className="my-4 text-sm text-nova-muted">Hiển thị <strong className="text-nova-text">{visible.length}</strong> / {affixes.length} Affix</p>
          {visible.length > 0 ? (
            <div className="grid gap-4 lg:grid-cols-2">
              {visible.map((affix) => <AffixCard key={affix.id} affix={affix} stoneSprite={stoneSprite} />)}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-nova-border px-5 py-12 text-center text-sm text-nova-muted">
              Không tìm thấy Affix phù hợp. Hãy thử từ khóa hoặc độ hiếm khác.
            </div>
          )}
        </div>
      </DstPanel>
    </section>
  );
}
