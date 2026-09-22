"use client";

import { useState } from "react";
import data from "@/app/data/pham-nhan-config.json";
import { normalizeSearchText } from "@/app/lib/wiki-search";
import { DstField, dstControlClassName } from "@/app/components/dst-field";

function compactChoiceLabel(label: string) {
  return label.replace(/\s*\(Mặc định\)/g, "");
}

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
      <p className="text-sm leading-6 text-nova-muted">Các tùy chọn còn trong menu Phàm Nhân {data.version}. Phím EVA theo cấp mở khóa: 1 Sinh Chi Hoa, 2 Tử Phong Tụ Linh, 3 Tinh Vũ Nguyệt Dực, 4 Dạ Du, 5 Trảm Linh. Lưỡi hái có 1000 độ bền và nạp bằng vũ khí. Chỉ số nền: 125 Máu, 125 Độ no, 200 Tinh thần; tốc độ, tiêu hao và sát thương x1.</p>
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
              <p className="mt-3 border-t border-nova-border pt-3 text-sm leading-6 text-nova-muted">
                {option.choices.map((choice) => compactChoiceLabel(choice.label)).join(" · ")}
              </p>
              <p className="mt-2 break-all text-xs text-nova-faint">Mã: <code>{option.key}</code></p>
            </article>
          );
        })}
      </div>
    </div>
  );
}
