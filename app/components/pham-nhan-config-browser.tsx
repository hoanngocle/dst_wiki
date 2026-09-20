"use client";

import { useState } from "react";
import data from "@/app/data/pham-nhan-config.json";
import { normalizeSearchText } from "@/app/lib/wiki-search";
import { DstField, dstControlClassName } from "@/app/components/dst-field";

export function PhamNhanConfigBrowser() {
  const [query, setQuery] = useState("");
  const [group, setGroup] = useState("Tất cả");
  const groups = [...new Set(data.options.map((option) => option.group))];
  const matches = data.options.filter((option) =>
    (group === "Tất cả" || option.group === group) &&
    normalizeSearchText([option.label, option.key, option.description, option.group].join(" ")).includes(normalizeSearchText(query)),
  );
  return (
    <div className="space-y-5">
      <p className="text-sm leading-6 text-nova-muted">Đây là cấu hình mặc định của Phàm Nhân {data.version}. Các giá trị trên trang dùng để tra cứu, không phải cấu hình đang chạy của máy chủ.</p>
      <div className="grid gap-4 sm:grid-cols-[1fr_240px]">
        <DstField label="Tìm config" htmlFor="config-query"><input id="config-query" type="search" value={query} onChange={(event) => setQuery(event.target.value)} className={dstControlClassName} placeholder="Tên tùy chọn hoặc nội dung…" /></DstField>
        <DstField label="Nhóm config" htmlFor="config-group"><select id="config-group" value={group} onChange={(event) => setGroup(event.target.value)} className={dstControlClassName}>{["Tất cả", ...groups].map((name) => <option key={name}>{name}</option>)}</select></DstField>
      </div>
      <p role="status" className="text-sm text-nova-muted">{matches.length} tùy chọn</p>
      {!matches.length && <p className="rounded-2xl border border-nova-border p-6">Không tìm thấy config phù hợp.</p>}
      <div className="grid items-start gap-4 lg:grid-cols-2">
        {matches.map((option) => {
          const defaultChoice = option.choices.find((choice) => choice.value === option.default);
          return (
            <article key={option.key} className="rounded-2xl border border-nova-border bg-nova-surface p-5">
              <p className="mb-2 text-xs font-semibold text-nova-accent">{option.group}</p>
              <h2 className="text-lg font-semibold">{option.label}</h2>
              {option.description && <p className="mt-2 whitespace-pre-line text-sm leading-6 text-nova-muted">{option.description}</p>}
              <p className="mt-3 text-sm"><strong>Mặc định:</strong> {defaultChoice?.label ?? String(option.default)}</p>
              <details className="mt-4 border-t border-nova-border pt-3">
                <summary className="cursor-pointer text-sm font-medium">Các giá trị có thể chọn ({option.choices.length})</summary>
                <ul className="mt-3 space-y-2 text-sm text-nova-muted">{option.choices.map((choice, index) => <li key={index} className="rounded-lg bg-nova-surface-soft px-3 py-2"><span className={choice.value === option.default ? "font-semibold text-nova-accent" : ""}>{choice.label}{choice.value === option.default ? " · Mặc định" : ""}</span>{choice.description && <p className="mt-1">{choice.description}</p>}</li>)}</ul>
                <p className="mt-3 break-all text-xs text-nova-faint">Mã cấu hình: <code>{option.key}</code></p>
              </details>
            </article>
          );
        })}
      </div>
    </div>
  );
}
