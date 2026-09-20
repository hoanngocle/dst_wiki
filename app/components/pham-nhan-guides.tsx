"use client";

import Link from "next/link";
import { useState } from "react";
import guides from "@/app/data/pham-nhan-guides.json";
import { normalizeSearchText } from "@/app/lib/wiki-search";
import { DstField, dstControlClassName } from "@/app/components/dst-field";

function plain(text: string) {
  return text.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/[*`]/g, "");
}

function GuideText({ text }: { text: string }) {
  const blocks = text.split(/\n\s*\n/);
  return <div className="space-y-4 text-sm leading-7 text-nova-muted">{blocks.map((block, index) => {
    if (block.startsWith("#")) return <h3 key={index} className="pt-2 text-base font-semibold text-nova-text">{plain(block.replace(/^#+\s*/, ""))}</h3>;
    if (block.startsWith("|")) {
      const rows = block.split("\n").filter((line) => line.startsWith("|") && !/^\|[\s:|\-]+\|$/.test(line)).map((line) => line.split("|").slice(1,-1).map((cell) => plain(cell.trim())));
      return <div key={index} className="overflow-x-auto"><table className="w-full min-w-96 border-collapse text-left"><thead><tr>{rows[0]?.map((cell, n) => <th key={n} className="border-b border-nova-border px-3 py-2 text-nova-text">{cell}</th>)}</tr></thead><tbody>{rows.slice(1).map((row, r) => <tr key={r}>{row.map((cell,c) => <td key={c} className="border-b border-nova-border px-3 py-2 align-top">{cell}</td>)}</tr>)}</tbody></table></div>;
    }
    if (block.startsWith("- ")) return <ul key={index} className="list-disc space-y-2 pl-5">{block.split(/\n- /).map((line,n) => <li key={n}>{plain(line.replace(/^- /,""))}</li>)}</ul>;
    return <p key={index} className="whitespace-pre-line">{plain(block)}</p>;
  })}</div>;
}

export function PhamNhanGuides() {
  const [query, setQuery] = useState("");
  const matches = guides.filter((guide) => normalizeSearchText(guide.title+" "+guide.text).includes(normalizeSearchText(query)));
  return <div className="space-y-4">
    <p className="text-sm leading-6 text-nova-muted">Solo đã được tích hợp đầy đủ trong Phàm Nhân. <Link href="/solo-leveling" className="font-semibold text-nova-accent underline">Xem Wiki kỹ năng, nhiệm vụ, quân đoàn và hầm ngục.</Link></p>
    <DstField label="Tìm hướng dẫn" htmlFor="guide-query"><input id="guide-query" type="search" className={dstControlClassName} value={query} onChange={(event) => setQuery(event.target.value)} /></DstField>
    <p role="status" className="text-sm text-nova-muted">{matches.length} chủ đề</p>
    {matches.map((guide) => <details key={guide.id} id={guide.id} className="rounded-2xl border border-nova-border bg-nova-surface p-5"><summary className="cursor-pointer text-lg font-semibold">{guide.title}</summary><div className="mt-4"><GuideText text={guide.text} /></div></details>)}
    {!matches.length && <p>Không tìm thấy hướng dẫn phù hợp.</p>}
  </div>;
}
