"use client";

import { useMemo, useState } from "react";

import type { CultivationStage } from "@/app/lib/cultivation-guide";
import type { ItemListEntry } from "@/app/lib/item-catalog";
import { GameSprite } from "./game-sprite";
import { ItemDetailModal } from "./item-detail-modal";
import { RecipeIngredients } from "./recipe-ingredients";

function StageRow({
  stage,
  itemsById,
  onSelectItem,
}: {
  stage: CultivationStage;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  return (
    <div
      role="row"
      aria-label={`Cảnh giới ${stage.rank}: ${stage.currentRealm} → ${stage.resultingRealm}`}
      className={`grid gap-4 p-4 lg:grid-cols-[4.5rem_11rem_15rem_11rem_minmax(0,1fr)] lg:items-center lg:gap-5 lg:px-5 ${stage.rank % 2 === 0 ? "bg-nova-surface-soft" : "bg-nova-surface"}`}
    >
      <div role="cell">
        <span className="grid size-11 place-items-center rounded-xl border border-nova-border bg-nova-surface-raised font-mono text-xs font-bold text-nova-accent lg:mx-auto">
          {String(stage.rank).padStart(2, "0")}
        </span>
      </div>
      <div role="cell" className="min-w-0">
        <p className="text-xs font-semibold tracking-[0.1em] text-nova-faint uppercase lg:hidden">
          Cảnh giới hiện tại
        </p>
        <h2 className="mt-1 text-base font-semibold tracking-[-0.02em] text-nova-text lg:mt-0">
          {stage.currentRealm}
        </h2>
      </div>
      <div role="cell" className="min-w-0">
        <p className="text-xs font-semibold tracking-[0.1em] text-nova-faint uppercase lg:hidden">
          Đan dược
        </p>
        <div className="mt-2 flex min-h-14 items-center gap-3 rounded-xl border border-nova-border bg-nova-surface-raised p-2 lg:mt-0">
          <GameSprite sprite={stage.pill.sprite} size={40} />
          <span className="text-sm font-semibold text-nova-text">{stage.pill.name}</span>
        </div>
      </div>
      <div role="cell" className="min-w-0">
        <p className="text-xs font-semibold tracking-[0.1em] text-nova-faint uppercase lg:hidden">
          Cảnh giới đạt được
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-2 lg:mt-0">
          <p className="text-base font-semibold tracking-[-0.02em] text-nova-text">
            {stage.resultingRealm}
          </p>
          {stage.breakthrough ? (
            <span className="rounded-full border border-nova-accent/30 bg-nova-accent/10 px-2 py-0.5 text-[0.62rem] font-semibold tracking-[0.08em] text-nova-accent uppercase">
              Đột phá
            </span>
          ) : null}
        </div>
      </div>
      <div role="cell" className="min-w-0">
        <p className="text-xs font-semibold tracking-[0.1em] text-nova-faint uppercase lg:hidden">
          Vật phẩm yêu cầu
        </p>
        <div className="mt-2 lg:mt-0">
          <RecipeIngredients
            recipe={stage.recipe}
            itemsById={itemsById}
            onSelectItem={onSelectItem}
          />
        </div>
      </div>
    </div>
  );
}

export function CultivationBrowser({
  stages,
  referenceItems,
}: {
  stages: readonly CultivationStage[];
  referenceItems: readonly ItemListEntry[];
}) {
  const [selectedItem, setSelectedItem] = useState<ItemListEntry | null>(null);
  const itemsById = useMemo(
    () => new Map(referenceItems.map((item) => [item.id, item] as const)),
    [referenceItems],
  );

  return (
    <>
      <div
        role="table"
        aria-label="Thứ tự cảnh giới Tu Tiên"
        className="overflow-hidden rounded-2xl border border-nova-border bg-nova-surface"
      >
        <div
          role="row"
          className="hidden bg-nova-surface-raised px-5 py-3 text-xs font-semibold tracking-[0.1em] text-nova-muted uppercase lg:grid lg:grid-cols-[4.5rem_11rem_15rem_11rem_minmax(0,1fr)] lg:gap-5"
        >
          <span role="columnheader" className="text-center">STT</span>
          <span role="columnheader">Cảnh giới hiện tại</span>
          <span role="columnheader">Đan dược</span>
          <span role="columnheader">Cảnh giới đạt được</span>
          <span role="columnheader">Vật phẩm yêu cầu</span>
        </div>
        <div className="divide-y divide-nova-border">
          {stages.map((stage) => (
            <StageRow
              key={stage.pillId}
              stage={stage}
              itemsById={itemsById}
              onSelectItem={setSelectedItem}
            />
          ))}
        </div>
      </div>

      {selectedItem ? (
        <ItemDetailModal
          item={selectedItem}
          itemsById={itemsById}
          onSelectItem={setSelectedItem}
          onClose={() => setSelectedItem(null)}
        />
      ) : null}
    </>
  );
}
