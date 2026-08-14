import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";

import type { CultivationStage } from "@/app/lib/cultivation-guide";
import type { ItemListEntry, ItemRecipe } from "@/app/lib/item-catalog";
import { CultivationBrowser } from "./cultivation-browser";

function item({
  id,
  name,
  namespace = "base_game",
  category = "item",
  recipe = null,
}: {
  id: string;
  name: string;
  namespace?: ItemListEntry["namespace"];
  category?: ItemListEntry["category"];
  recipe?: ItemRecipe | null;
}): ItemListEntry {
  return {
    id,
    prefabId: id.split(":")[1],
    namespace,
    category,
    name,
    englishName: null,
    description: null,
    craftingNote: null,
    sprite: null,
    recipe,
    wiki: null,
  };
}

it("opens resolved ingredients in one replaceable detail modal without hiding the stage", () => {
  const twigs = item({ id: "base_game:twigs", name: "Twigs" });
  const pigSkin = item({
    id: "base_game:pigskin",
    name: "Pig Skin",
    recipe: {
      outputCount: 1,
      ingredients: [{ id: twigs.id, name: twigs.name, amount: 2, sprite: null }],
    },
  });
  const pill = item({
    id: "tu_tien:xd_danyao_jq",
    name: "Tụ Khí Hoàn",
    namespace: "tu_tien",
    category: "pill",
    recipe: {
      outputCount: 1,
      ingredients: [{ id: pigSkin.id, name: pigSkin.name, amount: 3, sprite: null }],
    },
  });
  const stage: CultivationStage = {
    rank: 1,
    currentRealm: "Luyện Khí Sơ Kỳ",
    resultingRealm: "Luyện Khí Trung Kỳ",
    pillId: pill.id,
    breakthrough: false,
    pill,
    recipe: pill.recipe!,
  };

  render(
    <CultivationBrowser
      stages={[stage]}
      referenceItems={[pill, pigSkin, twigs]}
    />,
  );

  expect(
    screen.getByRole("row", {
      name: "Cảnh giới 1: Luyện Khí Sơ Kỳ → Luyện Khí Trung Kỳ",
    }),
  ).toBeDefined();
  expect(screen.getByText("Tụ Khí Hoàn")).toBeDefined();

  fireEvent.click(screen.getByRole("button", { name: "Pig Skin, số lượng 3" }));
  const pigSkinDialog = screen.getByRole("dialog", { name: "Pig Skin" });
  expect(pigSkinDialog).toBeDefined();

  fireEvent.click(
    within(pigSkinDialog).getByRole("button", { name: "Twigs, số lượng 2" }),
  );

  expect(screen.queryByRole("dialog", { name: "Pig Skin" })).toBeNull();
  expect(screen.getByRole("dialog", { name: "Twigs" })).toBeDefined();
  expect(screen.getByText("Tụ Khí Hoàn")).toBeDefined();
});
