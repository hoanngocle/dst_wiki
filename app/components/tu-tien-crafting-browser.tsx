"use client";

import { useState } from "react";
import type { ItemListEntry, ItemRecipe } from "@/app/lib/item-catalog";
import { WikiSearch } from "./wiki-search";
import { RecipeIngredients } from "./recipe-ingredients";
import { ItemDetailModal } from "./item-detail-modal";

export function TuTienCraftingBrowser({ furnaceItems, otherItems, referenceItems, dynamicRecipe }: {
  furnaceItems: readonly ItemListEntry[];
  otherItems: readonly ItemListEntry[];
  referenceItems: readonly ItemListEntry[];
  dynamicRecipe: ItemRecipe;
}) {
  const [furnace, setFurnace] = useState(true);
  const [selected, setSelected] = useState<ItemListEntry | null>(null);
  const byId = new Map(referenceItems.map(item => [item.id, item]));
  return <section aria-label="Danh sách chế tạo" className="mt-8">
    <div role="group" aria-label="Chọn nhóm chế tạo" className="mb-5 flex flex-wrap gap-3">
      {[{ active: true, label: `Đan Lô (${furnaceItems.length + 1})` }, { active: false, label: `Đồ chế khác của Hàn Lập (${otherItems.length})` }].map(option =>
        <button key={option.label} type="button" aria-pressed={furnace === option.active} onClick={() => setFurnace(option.active)} className={`min-h-11 rounded-full border px-5 py-2 font-semibold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent ${furnace === option.active ? "border-nova-accent text-nova-accent" : "border-nova-border text-nova-muted"}`}>{option.label}</button>
      )}
    </div>
    <h2 className="text-2xl font-semibold">{furnace ? "Lò Luyện Đan · Đan Lô" : "Đồ chế khác dành cho Hàn Lập"}</h2>
    <p className="mb-6 mt-2 text-nova-muted">{furnace ? "67 công thức đan dược, 10 pháp bảo và trang bị, cùng 1 công thức vũ khí chuyên thuộc. Bao gồm công thức của các nhân vật; một số món có điều kiện riêng." : "Các công thức khác có đường chế tạo và công dụng đã xác minh dành cho Hàn Lập."}</p>
    {furnace && <div className="mb-6 rounded-2xl border border-nova-border bg-nova-surface-soft p-5">
      <h3 className="mb-2 text-lg font-semibold">Vũ khí chuyên thuộc</h3>
      <p className="mb-4 text-sm text-nova-muted">Chưa xác nhận vũ khí đầu ra cho từng nhân vật. Nguyên liệu đã được đối chiếu; chưa xác nhận thời gian luyện.</p>
      <RecipeIngredients recipe={dynamicRecipe} itemsById={byId} onSelectItem={setSelected} />
    </div>}
    <WikiSearch key={furnace ? "furnace" : "other"} items={furnace ? furnaceItems : otherItems} referenceItems={referenceItems} hideSourceFilters />
    {selected && <ItemDetailModal item={selected} itemsById={byId} onClose={() => setSelected(null)} onSelectItem={setSelected} />}
  </section>;
}
