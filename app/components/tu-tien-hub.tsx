"use client";

import { useMemo, useState, useSyncExternalStore, type ReactNode } from "react";
import type { ItemListEntry, SpriteDescriptor } from "@/app/lib/item-catalog";
import { resolveTuTienTab, tuTienTabs, type TuTienTabId } from "@/app/lib/tu-tien-tabs";
import { GameSprite } from "./game-sprite";
import { TuTienDungeon } from "./tu-tien-dungeon";
import { TuTienAppearanceCards } from "./tu-tien-appearance-cards";
import { TuTienSkillTable } from "./tu-tien-skill-table";
import { TuTienGemTable } from "./tu-tien-gem-table";
import { TuTienStructures } from "./tu-tien-structures";
import { TuTienAchievements } from "./tu-tien-achievements";
import { RecipeIngredients } from "./recipe-ingredients";
import { ItemDetailModal } from "./item-detail-modal";

export type ModWikiEntry = {
  id: string;
  title: string;
  category: string;
  source: string;
  text: string[];
  facts: { label: string; value: string }[];
  ingredients: { prefab: string; amount: number }[];
};
export type ModWiki = {
  id: string;
  shortName: string;
  name: string;
  version: string;
  entries: ModWikiEntry[];
};

function normalize(value: string) {
  return value.normalize("NFD").replace(/\p{M}/gu, "").replace(/đ/gi, "d").toLocaleLowerCase("vi");
}

function ModCatalog({ mod, referenceItems, names, sprites }: { mod: ModWiki; referenceItems: readonly ItemListEntry[]; names: ReadonlyMap<string, string>; sprites: Readonly<Record<string, SpriteDescriptor>> }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(0);
  const [selected, setSelected] = useState<ItemListEntry | null>(null);
  const byId = useMemo(() => new Map(referenceItems.map(item => [item.id, item])), [referenceItems]);
  const byPrefab = useMemo(() => new Map(referenceItems.map(item => [item.prefabId, item])), [referenceItems]);
  const sprite = (row: ModWikiEntry) => sprites[row.id] ?? sprites[row.id.replace(/^(item|recipe):/, "")] ?? byPrefab.get(row.title)?.sprite;
  const title = (row: ModWikiEntry) => byPrefab.get(row.title)?.name ?? row.title;
  const entries = mod.entries.filter(row => mod.id !== "nyx" || row.category !== "Cảnh giới Nyx");
  const categories = [...new Set(entries.map(row => row.category))];
  const terms = normalize(query).trim().split(/\s+/).filter(Boolean);
  const rows = entries.filter(row => (!category || row.category === category) && terms.every(term => normalize([title(row), row.id, row.category, ...row.text, ...row.facts.map(f => `${f.label} ${f.value}`), ...row.ingredients.map(i => `${byPrefab.get(i.prefab)?.name ?? names.get(i.prefab) ?? i.prefab} ${i.prefab}`)].join(" ")).includes(term)));
  const gemTable = mod.id === "than-khi" && category === "Đá thuộc tính";
  const skillRows = mod.id === "nyx" ? rows.filter(row => row.category === "Kỹ năng") : [];
  const appearanceRows = mod.id === "nyx" ? rows.filter(row => row.category === "Ngoại hình") : [];
  const cardRows = mod.id === "nyx" ? rows.filter(row => !["Kỹ năng", "Ngoại hình"].includes(row.category)) : rows;
  const tableOnly = gemTable || (mod.id === "nyx" && ["Kỹ năng", "Ngoại hình"].includes(category));
  const pages = tableOnly ? 1 : Math.max(1, Math.ceil(cardRows.length / 20));
  const currentPage = Math.min(page, pages - 1);
  return <section className="mt-8" aria-label={mod.name}>
    <div className="flex flex-wrap items-baseline gap-3">
      <h2 className="text-2xl font-semibold">{mod.name}</h2>
      <span className="rounded-full bg-nova-surface-soft px-3 py-1 font-mono text-sm text-nova-muted">v{mod.version}</span>
    </div>
    <div className="my-5 flex flex-wrap gap-3">
      <input type="search" aria-label={`Tìm trong ${mod.name}`} placeholder="Tìm vật phẩm, kỹ năng, công thức, phần thưởng…" value={query} onChange={e => { setQuery(e.target.value); setPage(0); }} className="min-h-11 min-w-0 flex-1 rounded-xl border border-nova-border bg-nova-surface px-4" />
      <select aria-label={`Nhóm nội dung ${mod.name}`} value={category} onChange={e => { setCategory(e.target.value); setPage(0); }} className="min-h-11 max-w-full rounded-xl border border-nova-border bg-nova-surface px-4">
        <option value="">Tất cả nội dung</option>
        {categories.map(name => <option key={name} value={name}>{mod.id === "than-khi" && name === "Đá thuộc tính" ? "Đá Quý" : name}</option>)}
      </select>
    </div>
    <p role="status" className="mb-4 text-sm text-nova-muted">{rows.length} / {entries.length} mục{tableOnly ? "" : ` · Trang ${currentPage + 1}/${pages}`}</p>
    {skillRows.length ? <TuTienSkillTable rows={skillRows} sprites={sprites} /> : null}
    {appearanceRows.length ? <TuTienAppearanceCards rows={appearanceRows} sprites={sprites} /> : null}
    {gemTable ? <TuTienGemTable rows={rows} sprites={sprites} /> : <div className="grid gap-4 lg:grid-cols-2">
      {cardRows.slice(currentPage * 20, currentPage * 20 + 20).map(row => <article key={row.id} className="min-w-0 rounded-2xl border border-nova-border bg-nova-surface-soft p-5">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-nova-muted">{row.category}</p>
        <div className="flex items-center gap-3">{sprite(row) ? <GameSprite sprite={sprite(row)!} size={56} label={`Ảnh ${title(row)}`} /> : null}<h3 className="text-lg font-semibold">{title(row)}</h3></div>
        {row.text.map((text, index) => <p key={index} className="mt-3 whitespace-pre-line break-words text-sm leading-6 text-nova-muted">{text}</p>)}
        {row.facts.length ? <dl className="mt-4 space-y-2 text-sm">{row.facts.map((f, index) => <div key={index} className="flex flex-wrap justify-between gap-x-4 gap-y-1 border-b border-nova-border/60 pb-2"><dt className="text-nova-muted">{f.label}</dt><dd className="min-w-0 break-words font-medium">{f.value}</dd></div>)}</dl> : null}
        {row.ingredients.length ? <div className="mt-4">
          <p className="mb-2 text-sm font-semibold">{row.category === "Phần thưởng" ? "Vật phẩm nhận được" : "Nguyên liệu"}</p>
          <RecipeIngredients recipe={{ outputCount: 1, ingredients: row.ingredients.map(ingredient => {
            const item = byPrefab.get(ingredient.prefab);
            return { id: item?.id ?? ingredient.prefab, name: item?.name ?? names.get(ingredient.prefab) ?? ingredient.prefab, amount: ingredient.amount, sprite: item?.sprite ?? sprites[ingredient.prefab] ?? null };
          }) }} itemsById={byId} onSelectItem={setSelected} />
        </div> : null}
        <details className="mt-4 text-xs text-nova-faint"><summary className="cursor-pointer">Nguồn đối chiếu</summary><p className="mt-2 break-all">{row.source}</p></details>
      </article>)}
    </div>}
    {rows.length === 0 ? <p className="py-8 text-nova-muted">Không tìm thấy nội dung phù hợp.</p> : null}
    {pages > 1 ? <div className="mt-5 flex items-center justify-between gap-3">
      <button type="button" disabled={currentPage === 0} onClick={() => setPage(currentPage - 1)} className="min-h-11 rounded-full border border-nova-border px-5 disabled:opacity-40">Trước</button>
      <button type="button" disabled={currentPage === pages - 1} onClick={() => setPage(currentPage + 1)} className="min-h-11 rounded-full border border-nova-border px-5 disabled:opacity-40">Sau</button>
    </div> : null}
    {selected ? <ItemDetailModal item={selected} itemsById={byId} onClose={() => setSelected(null)} onSelectItem={setSelected} /> : null}
  </section>;
}

function subscribe(listener: () => void) {
  window.addEventListener("hashchange", listener);
  window.addEventListener("popstate", listener);
  window.addEventListener("tu-tien-tab", listener);
  return () => {
    window.removeEventListener("hashchange", listener);
    window.removeEventListener("popstate", listener);
    window.removeEventListener("tu-tien-tab", listener);
  };
}

export function TuTienHub({ crafting, cultivation, mods, referenceItems, sprites }: { crafting: ReactNode; cultivation: ReactNode; mods: readonly ModWiki[]; referenceItems: readonly ItemListEntry[]; sprites: Readonly<Record<string, SpriteDescriptor>> }) {
  const active = useSyncExternalStore(subscribe, () => resolveTuTienTab(window.location.hash), () => "che-tao" as TuTienTabId);
  function select(id: TuTienTabId) {
    window.history.pushState(null, "", `/tu-tien#${id}`);
    window.dispatchEvent(new Event("tu-tien-tab"));
  }
  const names = useMemo(() => new Map(mods.flatMap(mod => mod.entries.filter(row => ["Vật phẩm", "Công thức", "Trang bị", "Linh dược"].includes(row.category)).map(row => [row.id.replace(/^(item|recipe):/, ""), row.title] as const))), [mods]);
  const mod = mods.find(item => item.id === active);
  return <div className="mt-8">
    <div role="tablist" aria-label="Các mục Tu Tiên" className="flex flex-wrap gap-2 border-b border-nova-border pb-5">
      {tuTienTabs.map((tab, index) => <button type="button" role="tab" id={`tab-${tab.id}`} key={tab.id} aria-selected={active === tab.id} aria-controls={`panel-${tab.id}`} tabIndex={active === tab.id ? 0 : -1} onClick={() => select(tab.id)} onKeyDown={event => {
        const next = event.key === "ArrowRight" ? (index + 1) % tuTienTabs.length : event.key === "ArrowLeft" ? (index - 1 + tuTienTabs.length) % tuTienTabs.length : event.key === "Home" ? 0 : event.key === "End" ? tuTienTabs.length - 1 : null;
        if (next !== null) { event.preventDefault(); select(tuTienTabs[next].id); document.getElementById(`tab-${tuTienTabs[next].id}`)?.focus(); }
      }} className={`min-h-11 rounded-full border px-4 py-2 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent ${active === tab.id ? "border-nova-accent bg-nova-accent text-white" : "border-nova-border text-nova-muted hover:text-nova-text"}`}>{tab.label}</button>)}
    </div>
    <div role="tabpanel" id={`panel-${active}`} aria-labelledby={`tab-${active}`} tabIndex={0}>
      {active === "che-tao" ? crafting : active === "canh-gioi" ? cultivation : active === "cong-trinh" ? <TuTienStructures referenceItems={referenceItems} sprites={sprites} /> : active === "thanh-tuu" && mod ? <TuTienAchievements mod={mod} /> : active === "ham-nguc" && mod ? <TuTienDungeon mod={mod} referenceItems={referenceItems} names={names} sprites={sprites} /> : mod ? <ModCatalog key={mod.id} mod={mod} referenceItems={referenceItems} names={names} sprites={sprites} /> : null}
    </div>
  </div>;
}
