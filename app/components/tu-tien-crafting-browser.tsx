"use client";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { WikiSearch } from "./wiki-search";

export function TuTienCraftingBrowser({ furnaceItems, otherItems, referenceItems }: {
  furnaceItems: readonly ItemListEntry[];
  otherItems: readonly ItemListEntry[];
  referenceItems: readonly ItemListEntry[];
}) {
  const items = [...new Map([...furnaceItems, ...otherItems].map(item => [item.id, item])).values()];
  return <section aria-label="Danh sách chế tạo" className="mt-8">
    <WikiSearch items={items} referenceItems={referenceItems} hideSourceFilters />
  </section>;
}
