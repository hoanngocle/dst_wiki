"use client";

import { useMemo, useState, type ReactNode } from "react";
import data from "@/data/generated/tu-tien-structures.json";
import type { ItemListEntry, SpriteDescriptor } from "@/app/lib/item-catalog";
import { GameSprite } from "./game-sprite";
import { RecipeIngredients } from "./recipe-ingredients";
import { ItemDetailModal } from "./item-detail-modal";

const number = (value: number) => value.toLocaleString("vi-VN", { maximumFractionDigits: 4 });
const percent = (value: number) => `${number(value * 100)}%`;
const fold = (value: string) => value.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase().replaceAll("đ", "d");
const weightTotal = data.treasureGroups.reduce((sum, group) => sum + group.weight, 0);
const totals = new Map<string, number>();
for (const group of data.treasureGroups) {
  for (const prefab of group.prefabs) totals.set(prefab, (totals.get(prefab) ?? 0) + group.weight / weightTotal / group.prefabs.length);
}

function WikiTable({ label, headers, children }: { label: string; headers: string[]; children: ReactNode }) {
  return <div className="mt-3 max-h-96 overflow-auto rounded-xl border border-nova-border">
    <table aria-label={label} className="w-full text-left text-sm">
      <thead className="sticky top-0 z-10 bg-nova-surface"><tr>{headers.map(header => <th key={header} scope="col" className="border-b border-nova-border px-4 py-3 font-semibold">{header}</th>)}</tr></thead>
      <tbody className="divide-y divide-nova-border">{children}</tbody>
    </table>
  </div>;
}
const cell = "px-4 py-3 align-top";

export function TuTienStructures({ referenceItems, sprites }: { referenceItems: readonly ItemListEntry[]; sprites: Readonly<Record<string, SpriteDescriptor>> }) {
  const [query, setQuery] = useState("");
  const [group, setGroup] = useState("");
  const [selected, setSelected] = useState<ItemListEntry | null>(null);
  const byPrefab = useMemo(() => new Map(referenceItems.map(item => [item.prefabId, item])), [referenceItems]);
  const byId = useMemo(() => new Map(referenceItems.map(item => [item.id, item])), [referenceItems]);
  const name = (prefab: string) => byPrefab.get(prefab)?.name ?? (data.names as Record<string, string>)[prefab] ?? prefab;
  const icon = (prefab: string) => sprites[prefab] ?? sprites[(data.spriteAliases as Record<string, string>)[prefab]] ?? byPrefab.get(prefab)?.sprite;
  const matches = (text: string) => fold(text).includes(fold(query.trim()));
  const rows = data.entries.filter(entry => (!group || entry.group === group) && (
    matches([entry.name, entry.prefab, ...entry.usage, ...entry.recipes.flatMap(recipe => recipe.ingredients.map(i => `${i.prefab} ${name(i.prefab)}`))].join(" ")) ||
    (entry.group === "Máy Tái Luyện" && data.prices.some(p => matches(`${p.prefab} ${name(p.prefab)}`))) ||
    (entry.group === "Kho báu" && data.treasureGroups.some(g => g.prefabs.some(p => matches(`${p} ${name(p)}`))))
  ));
  function ItemCell({ prefab }: { prefab: string }) {
    const item = byPrefab.get(prefab);
    const content = <><GameSprite sprite={icon(prefab) ?? null} size={28} label={`Ảnh ${name(prefab)}`} /><span>{name(prefab)}</span></>;
    return item ? <button type="button" onClick={() => setSelected(item)} className="inline-flex min-h-9 items-center gap-2 text-left hover:text-nova-accent">{content}</button> : <span className="inline-flex items-center gap-2">{content}</span>;
  }
  return <section className="mt-8" aria-label="Công Trình Tu Tiên">
    <div className="flex flex-wrap items-baseline gap-3"><h2 className="text-2xl font-semibold">Công Trình</h2><span className="rounded-full bg-nova-surface-soft px-3 py-1 font-mono text-sm text-nova-muted">v{data.version}</span></div>
    <div className="my-5 flex flex-wrap gap-3">
      <input type="search" aria-label="Tìm công trình và vật phẩm" value={query} onChange={e => setQuery(e.target.value)} placeholder="Tìm công trình, vật phẩm, nguyên liệu…" className="min-h-11 min-w-0 flex-1 rounded-xl border border-nova-border bg-nova-surface px-4" />
      <select aria-label="Nhóm công trình" value={group} onChange={e => setGroup(e.target.value)} className="min-h-11 max-w-full rounded-xl border border-nova-border bg-nova-surface px-4"><option value="">Tất cả công trình & vật phẩm</option>{[...new Set(data.entries.map(e => e.group))].map(g => <option key={g}>{g}</option>)}</select>
    </div>
    <p role="status" className="mb-4 text-sm text-nova-muted">{rows.length} / {data.entries.length} công trình & vật phẩm</p>
    <div className="grid gap-4 lg:grid-cols-2">
      {rows.map(entry => <article key={entry.prefab} className={`min-w-0 rounded-2xl border border-nova-border bg-nova-surface-soft p-5 ${["Máy Tái Luyện", "Kho báu"].includes(entry.group) ? "lg:col-span-2" : ""}`}>
        <p className="mb-2 text-xs uppercase tracking-wide text-nova-muted">{entry.group}</p>
        <div className="flex items-center gap-3">{icon(entry.prefab) ? <GameSprite sprite={icon(entry.prefab)!} size={56} label={`Ảnh ${entry.name}`} /> : null}<h3 className="text-lg font-semibold">{entry.name}</h3></div>
        <h4 className="mt-5 font-semibold">Công thức chế tạo</h4>
        {entry.recipes.map((recipe, index) => <div key={index} className="mt-3 rounded-xl border border-nova-border p-4">
          {entry.recipes.length > 1 ? <p className="mb-2 font-semibold">Cách {index + 1}</p> : null}
          <p className="mb-2 text-sm text-nova-muted">{recipe.technology} · Nhận được: {recipe.outputCount}</p>
          <RecipeIngredients itemsById={byId} onSelectItem={setSelected} recipe={{ outputCount: recipe.outputCount, ingredients: recipe.ingredients.map(i => {
            const item = byPrefab.get(i.prefab);
            return { id: item?.id ?? i.prefab, name: name(i.prefab), amount: i.amount, sprite: icon(i.prefab) ?? null };
          }) }} />
          {recipe.condition ? <p className="mt-3 text-sm leading-6 text-nova-muted">{recipe.condition}</p> : null}
        </div>)}
        <h4 className="mt-5 font-semibold">Hướng dẫn sử dụng</h4>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm leading-6 text-nova-muted">{entry.usage.map((text,index) => <li key={index}>{text}</li>)}</ol>
        {entry.group === "Máy Tái Luyện" ? <>
          <h4 className="mt-5 font-semibold">Bảng giá tái luyện</h4>
          <p className="mt-2 text-sm text-nova-muted">Đơn vị: Linh Thạch Hạ Phẩm mỗi món, độ bền 100%. Giá mặc định cho món chưa có giá riêng hoặc công thức: {data.defaultPrice}.</p>
          <WikiTable label="Bảng giá nền Máy Tái Luyện" headers={["Vật phẩm", "Giá nền / món"]}>{data.prices.filter(p => !query.trim() || matches(`${p.prefab} ${name(p.prefab)}`) || matches(entry.name)).map(p => <tr key={p.prefab}><td className={cell}><ItemCell prefab={p.prefab} /></td><td className={`${cell} tabular-nums`}>{number(p.stones)}</td></tr>)}</WikiTable>
          <h4 className="mt-5 font-semibold">Đá thuộc tính</h4>
          <WikiTable label="Giá đá thuộc tính" headers={["Bậc đá", "Hạ Phẩm / món"]}>{data.attributePrices.map(p => <tr key={p.tier}><td className={cell}>{p.tier === "UTILITY" ? "Tiện ích" : p.tier}</td><td className={cell}>{number(p.stones)}</td></tr>)}</WikiTable>
          <p className="mt-2 text-sm text-nova-muted">Đá dùng prefab hh_effect_stone; giá theo mã thuộc tính đã lưu trên đá hợp lệ.</p>
        </> : null}
        {entry.group === "Kho báu" ? <>
          <h4 className="mt-5 font-semibold">Tỷ lệ kho báu</h4>
          <p className="mt-2 text-sm leading-6 text-nova-muted">Game chỉ tính các prefab có sẵn. Bảng giả định toàn bộ pool được đăng ký: tổng trọng số {weightTotal}. Trong nhóm, mỗi kết quả có cơ hội bằng nhau; nhóm trống bị bỏ và tỷ lệ được tính lại. Mỗi lần đào tạo 1 vật phẩm hoặc 1 sinh vật.</p>
          <WikiTable label="Tỷ lệ nhóm kho báu" headers={["Loại", "Trọng số", "Số kết quả", "Tỷ lệ nhóm"]}>{data.treasureGroups.map(g => <tr key={g.id}><th scope="row" className={cell}>{g.name}</th><td className={cell}>{g.weight}</td><td className={cell}>{g.prefabs.length}</td><td className={cell}>{percent(g.weight / weightTotal)}</td></tr>)}</WikiTable>
          <div className="mt-5 grid gap-5 xl:grid-cols-2">{data.treasureGroups.map(g => <section key={g.id}>
            <h4 className="font-semibold">{g.name} · {percent(g.weight / weightTotal)}</h4>
            <WikiTable label={`Vật phẩm kho báu ${g.name}`} headers={[g.id === "boss" || g.id === "monster" ? "Sinh vật" : "Vật phẩm", "Trong nhóm", "Nhánh / lần đào"]}>{g.prefabs.filter(p => !query.trim() || matches(`${p} ${name(p)}`) || matches(entry.name)).map(p => <tr key={p}><td className={cell}><ItemCell prefab={p} /></td><td className={cell}>{percent(1 / g.prefabs.length)}</td><td className={cell}>{percent(g.weight / weightTotal / g.prefabs.length)}</td></tr>)}</WikiTable>
          </section>)}</div>
          <h4 className="mt-5 font-semibold">Tổng tỷ lệ từng kết quả</h4>
          <p className="mt-2 text-sm text-nova-muted">Cộng xác suất của các nhánh khi một prefab xuất hiện trong nhiều nhóm, như amulet và lunarthrall_plant.</p>
          <WikiTable label="Tổng tỷ lệ từng kết quả kho báu" headers={["Kết quả", "Tỷ lệ / lần đào"]}>{[...totals].filter(([p]) => !query.trim() || matches(`${p} ${name(p)}`) || matches(entry.name)).map(([p,rate]) => <tr key={p}><td className={cell}><ItemCell prefab={p} /></td><td className={cell}>{percent(rate)}</td></tr>)}</WikiTable>
        </> : null}
        <details className="mt-4 text-xs text-nova-muted"><summary className="cursor-pointer">Nguồn đối chiếu</summary>{entry.sources.map(source => <p key={source} className="mt-2 break-all">{source}</p>)}</details>
      </article>)}
    </div>
    {!rows.length ? <p className="py-8 text-nova-muted">Không tìm thấy công trình hoặc vật phẩm phù hợp.</p> : null}
    {selected ? <ItemDetailModal item={selected} itemsById={byId} onClose={() => setSelected(null)} onSelectItem={setSelected} /> : null}
  </section>;
}
