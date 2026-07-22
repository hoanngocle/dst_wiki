import { describe, expect, it } from "vitest";

import type { ItemListEntry } from "./item-catalog";
import { selectCharacters } from "./character-catalog";

function createItem(
  id: string,
  namespace: ItemListEntry["namespace"],
  category: ItemListEntry["category"],
): ItemListEntry {
  return {
    id,
    prefabId: id.split(":")[1],
    namespace,
    category,
    name: id,
    englishName: null,
    description: null,
    craftingNote: null,
    sprite: null,
    recipe: null,
    wiki: null,
  };
}

describe("selectCharacters", () => {
  it("keeps playable characters from both DST and Tu Tien", () => {
    const items = [
      createItem("base_game:wigfrid", "base_game", "character"),
      createItem("tu_tien:xd_hantianzun", "tu_tien", "character"),
      createItem("base_game:log", "base_game", "item"),
    ];

    expect(selectCharacters(items).map((item) => item.id)).toEqual([
      "base_game:wigfrid",
      "tu_tien:xd_hantianzun",
    ]);
  });
});
