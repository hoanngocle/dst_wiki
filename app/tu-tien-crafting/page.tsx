import type { Metadata } from "next";

import { DstHero } from "@/app/components/dst-hero";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { WikiSearch } from "@/app/components/wiki-search";
import { parseItemPayload } from "@/app/lib/item-catalog";
import {
  type CraftingExclusionReason,
  type HanLapCraftingSelection,
  selectHanLapCraftables,
} from "@/app/lib/tu-tien-crafting";
import catalogPayload from "@/public/data/catalog.json";
import itemsPayload from "@/public/data/items.json";

export const metadata: Metadata = {
  title: "Đồ chế Tu Tiên của Hàn Lập | DST Wiki",
  description: "Danh mục đồ chế Tu Tiên đã xác minh dành cho Hàn Lập.",
};

const allItems = parseItemPayload(itemsPayload);
const selection = selectHanLapCraftables(allItems, catalogPayload);

const exclusionReasons: readonly CraftingExclusionReason[] = [
  "no_recipe",
  "other_character",
  "no_verified_use",
  "unresolved_ingredient",
];

export function assertNonEmptySelection(
  candidate: HanLapCraftingSelection,
): asserts candidate is HanLapCraftingSelection {
  if (candidate.items.length > 0) return;

  const counts = new Map<CraftingExclusionReason, number>(
    exclusionReasons.map((reason) => [reason, 0]),
  );
  for (const excluded of candidate.excluded) {
    counts.set(excluded.reason, (counts.get(excluded.reason) ?? 0) + 1);
  }
  const diagnosticCounts = exclusionReasons
    .map((reason) => `${reason}=${counts.get(reason) ?? 0}`)
    .join(", ");

  throw new Error(
    `Hàn Lập crafting selection invariant failed: selected=0, excluded=${candidate.excluded.length}; ${diagnosticCounts}`,
  );
}

assertNonEmptySelection(selection);

export default function HanLapCraftingPage() {
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader active="tu-tien-crafting" />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <DstHero
            testId="han-lap-crafting-hero"
            eyebrow="Tu Tiên · Chế tạo Hàn Lập"
            title="Đồ chế Tu Tiên của Hàn Lập"
            description="Chỉ liệt kê vật phẩm có đường chế tạo và công dụng đã được xác minh."
            stats={[{ label: "Đồ chế đã xác minh", value: selection.items.length }]}
            statsAriaLabel="Tổng quan đồ chế Tu Tiên"
          />
          <WikiSearch
            items={selection.items}
            referenceItems={allItems}
            hideSourceFilters
          />
        </div>
      </DstPageShell>
    </div>
  );
}
