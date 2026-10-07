"use client";

import { useState, type ReactNode } from "react";
import type { ModWiki, ModWikiEntry } from "./tu-tien-hub";

const fact = (entry: ModWikiEntry, label: string) => entry.facts.find(f => f.label === label)?.value ?? "—";
const fold = (text: string) => text.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase().replaceAll("đ", "d");
const cell = "border-b border-nova-border px-4 py-3 align-top";
type Column = { label: string; render: (entry: ModWikiEntry) => ReactNode };

function LookupTable({ title, searchLabel, rows, columns, seasonFilter = false }: { title: string; searchLabel: string; rows: readonly ModWikiEntry[]; columns: Column[]; seasonFilter?: boolean }) {
  const [query, setQuery] = useState("");
  const [season, setSeason] = useState("");
  const results = rows.filter(row => (!season || fact(row, "Mùa") === season) && fold([row.title, row.id, ...row.text, ...row.facts.map(f => `${f.label} ${f.value}`)].join(" ")).includes(fold(query.trim())));
  return <section className="mt-8" aria-label={title}>
    <h3 className="text-xl font-semibold">{title}</h3>
    <div className="my-4 flex flex-wrap gap-3">
      <input type="search" aria-label={searchLabel} value={query} onChange={e => setQuery(e.target.value)} placeholder="Tìm tên, điều kiện, hiệu ứng…" className="min-h-11 min-w-0 flex-1 rounded-xl border border-nova-border bg-nova-surface px-4" />
      {seasonFilter ? <select aria-label="Mùa nhiệm vụ" value={season} onChange={e => setSeason(e.target.value)} className="min-h-11 rounded-xl border border-nova-border bg-nova-surface px-4"><option value="">Tất cả mùa</option>{["Xuân", "Hạ", "Thu", "Đông"].map(s => <option key={s}>{s}</option>)}</select> : null}
    </div>
    <p role="status" className="mb-3 text-sm text-nova-muted">{results.length} / {rows.length} mục</p>
    <div className="max-h-[70vh] overflow-auto rounded-2xl border border-nova-border">
      <table aria-label={title} className="w-full min-w-[700px] text-left text-sm">
        <thead className="sticky top-0 z-10 bg-nova-surface"><tr>{columns.map(column => <th key={column.label} scope="col" className={`${cell} whitespace-nowrap font-semibold`}>{column.label}</th>)}<th scope="col" className={cell}>Nguồn</th></tr></thead>
        <tbody>{results.map(row => <tr key={row.id} className="bg-nova-surface-soft hover:bg-nova-surface">{columns.map((column, index) => index === 0 ? <th key={column.label} scope="row" className={`${cell} min-w-40 font-medium`}>{column.render(row)}</th> : <td key={column.label} className={`${cell} ${index === 1 ? "min-w-64" : ""}`}>{column.render(row)}</td>)}<td className={cell}><details><summary className="cursor-pointer text-nova-muted">Đối chiếu</summary><p className="mt-2 max-w-64 break-all text-xs text-nova-muted">{row.source}</p></details></td></tr>)}</tbody>
      </table>
    </div>
    {!results.length ? <p className="mt-3 text-sm text-nova-muted">Không tìm thấy kết quả phù hợp.</p> : null}
  </section>;
}

export function TuTienAchievements({ mod }: { mod: ModWiki }) {
  const quests = mod.entries.filter(e => e.category === "Nhiệm vụ mùa");
  const achievements = mod.entries.filter(e => e.category === "Thành tựu");
  const caps = new Map(mod.entries.filter(e => e.category === "Giới hạn đặc quyền").map(e => [e.id.replace(/^cap:/, ""), fact(e, "Số lần tối đa")]));
  const perks = mod.entries.filter(e => e.category === "Đặc quyền").map(e => ({ ...e, facts: [...e.facts, { label: "Giới hạn", value: caps.get(e.id.replace(/^perk:/, "")) ?? "—" }] }));
  const rewards = mod.entries.filter(e => e.category === "Rương nhiệm vụ");
  const seasons = [{ id: "spring", name: "Xuân" }, { id: "summer", name: "Hạ" }, { id: "autumn", name: "Thu" }, { id: "winter", name: "Đông" }];
  const description = (row: ModWikiEntry) => <div className="space-y-1 leading-6 text-nova-muted">{row.text.map((text,index) => <p key={index}>{text}</p>)}</div>;
  return <section className="mt-8" aria-label={mod.name}>
    <div className="flex flex-wrap items-baseline gap-3"><h2 className="text-2xl font-semibold">{mod.name}</h2><span className="rounded-full bg-nova-surface-soft px-3 py-1 font-mono text-sm text-nova-muted">v{mod.version}</span></div>
    <LookupTable title="Bảng nhiệm vụ" searchLabel="Tìm nhiệm vụ" rows={quests} seasonFilter columns={[
      { label: "Nhiệm vụ", render: row => row.title },
      { label: "Yêu cầu", render: description },
      { label: "Mùa", render: row => fact(row, "Mùa") },
      { label: "Mục tiêu", render: row => fact(row, "Mục tiêu") },
    ]} />
    <p className="mt-4 text-sm leading-6 text-nova-muted">Mỗi lượt có 6 nhiệm vụ và 4 rương thưởng, mở ở các mốc hoàn thành 1, 2, 4 và 6 nhiệm vụ.</p>
    <details className="mt-4 rounded-xl border border-nova-border bg-nova-surface-soft p-4"><summary className="cursor-pointer font-semibold">Phần thưởng mốc nhiệm vụ</summary>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">{seasons.map(season => <section key={season.id}><h4 className="font-semibold">Mùa {season.name}</h4>{[1,2,4,6].map(milestone => {
        const pool = rewards.filter(row => fact(row,"Mùa") === season.id && fact(row,"Nhiệm vụ hoàn thành") === String(milestone));
        return <div key={milestone} className="mt-3"><p className="text-sm font-medium">Hoàn thành {milestone} nhiệm vụ</p><ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-6 text-nova-muted">{pool.map(row => <li key={row.id}>{row.title}{row.facts.filter(f => !["Mùa", "Nhiệm vụ hoàn thành"].includes(f.label)).map(f => ` · ${f.label}: ${f.value}`).join("")}{row.ingredients.length ? ` · ${row.ingredients.map(i => `${i.prefab} ×${i.amount}`).join(", ")}` : ""}</li>)}</ul></div>;
      })}</section>)}</div>
    </details>
    <LookupTable title="Bảng Thành tựu" searchLabel="Tìm thành tựu" rows={achievements} columns={[
      { label: "Thành tựu", render: row => row.title },
      { label: "Điều kiện", render: description },
      { label: "Mục tiêu", render: row => fact(row, "Mục tiêu") },
      { label: "Sao thưởng", render: row => fact(row, "Sao thưởng") },
    ]} />
    <LookupTable title="Bảng Perk" searchLabel="Tìm Perk" rows={perks} columns={[
      { label: "Perk", render: row => row.title },
      { label: "Hiệu ứng", render: description },
      { label: "Giá Sao", render: row => fact(row, "Giá Sao") },
      { label: "Hệ số giá", render: row => fact(row, "Hệ số giá") },
      { label: "Số lần tối đa", render: row => fact(row, "Giới hạn") },
    ]} />
    <p className="mt-3 text-sm text-nova-muted">Giá Sao là giá gốc trong source. Dấu — nghĩa là dữ liệu không ghi hệ số hoặc giới hạn riêng.</p>
  </section>;
}
