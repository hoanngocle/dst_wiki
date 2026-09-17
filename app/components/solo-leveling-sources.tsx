"use client";

import { useState } from "react";
import { DstField, dstControlClassName } from "@/app/components/dst-field";
import { DstPanel } from "@/app/components/dst-panel";
import { normalizeSoloSearch, type SoloLevelingData } from "@/app/lib/solo-leveling";

export function SoloLevelingSources({ files }: { files: SoloLevelingData["files"] }) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState("Wiki.txt");
  const [sources, setSources] = useState<Record<string, string> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [opened, setOpened] = useState(false);
  const file = files.find((item) => item.path === selected);
  const filteredFiles = files.filter((item) => normalizeSoloSearch(item.path).includes(normalizeSoloSearch(query)));

  async function openSource() {
    setOpened(true);
    if (sources || !file?.text || loading) return;
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/solo-leveling/sources.json");
      if (!response.ok) throw new Error("Không tải được file nguồn. Hãy thử lại.");
      setSources(await response.json());
    } catch {
      setError("Không tải được file nguồn. Hãy thử lại hoặc tải bộ nguồn ZIP.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div id="solo-sources" className="mt-8 scroll-mt-6"><DstPanel className="p-5 sm:p-6">
      <h2 className="text-2xl font-semibold tracking-[-0.03em]">File nguồn & tài liệu gốc</h2>
      <p className="mt-2 text-sm leading-6 text-nova-muted">
        Tra cứu {files.length} file trong thư mục mod. Đọc đầy đủ Lua, XML và tài liệu văn bản ngay bên dưới.
        File animation, texture và âm thanh được liệt kê kèm dung lượng.
      </p>
      <div className="mt-4 flex flex-wrap gap-3 text-sm font-semibold text-nova-accent">
        <a className="underline underline-offset-4" href="/solo-leveling/Wiki.txt" download>Tải Wiki.txt gốc</a>
        <a className="underline underline-offset-4" href="/solo-leveling/solo-leveling-sources.zip" download>Tải bộ nguồn văn bản ZIP</a>
      </div>
      <div className="mt-6 grid items-end gap-4 sm:grid-cols-2">
        <DstField label="Tìm file nguồn" htmlFor="solo-source-search">
          <input id="solo-source-search" className={dstControlClassName} type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="daily, recipe, prefab…" />
        </DstField>
        <DstField label="Chọn file" htmlFor="solo-source-file">
          <select id="solo-source-file" className={dstControlClassName} value={selected} onChange={(event) => { setSelected(event.target.value); setOpened(false); }}>
            {!filteredFiles.some((item) => item.path === selected) && <option value={selected}>{selected}</option>}
            {filteredFiles.map((item) => <option key={item.path} value={item.path}>{item.path}</option>)}
          </select>
        </DstField>
      </div>
      <p className="mt-3 break-all text-xs leading-5 text-nova-faint">{filteredFiles.length} file khớp · File đang chọn: {selected} · {file?.size.toLocaleString("vi-VN")} byte</p>
      <button type="button" disabled={loading} onClick={openSource} className="mt-4 min-h-11 cursor-pointer rounded-xl bg-nova-accent px-4 text-sm font-semibold text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-nova-accent disabled:opacity-60">
        {loading ? "Đang tải…" : "Đọc file đã chọn"}
      </button>
      {error && <p role="alert" className="mt-4 text-sm text-nova-muted">{error}</p>}
      {opened && !file?.text && <p className="mt-4 text-sm text-nova-muted">Đây là file nhị phân ({selected.split(".").at(-1)}), không có nội dung văn bản để đọc.</p>}
      {opened && file?.text && sources?.[selected] !== undefined && (
        <pre aria-label={`Nội dung ${selected}`} tabIndex={0} className="mt-4 max-h-[36rem] overflow-auto rounded-xl border border-nova-border bg-nova-surface-soft p-4 text-xs leading-6 text-nova-muted"><code>{sources[selected]}</code></pre>
      )}
    </DstPanel></div>
  );
}
