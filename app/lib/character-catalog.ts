import type { ItemListEntry } from "./item-catalog";

export function selectCharacters(
  items: readonly ItemListEntry[],
): ItemListEntry[] {
  return items.filter((item) => item.category === "character");
}
