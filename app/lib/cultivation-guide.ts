import type { ItemListEntry, ItemRecipe } from "./item-catalog";

type CultivationStageDefinition = {
  currentRealm: string;
  resultingRealm: string;
  pillId: string;
  breakthrough: boolean;
};

export type CultivationStage = CultivationStageDefinition & {
  rank: number;
  pill: ItemListEntry;
  recipe: ItemRecipe;
};

const cultivationStageDefinitions: readonly CultivationStageDefinition[] = [
  { currentRealm: "Luyện Khí Sơ Kỳ", resultingRealm: "Luyện Khí Trung Kỳ", pillId: "tu_tien:xd_danyao_jq", breakthrough: false },
  { currentRealm: "Luyện Khí Trung Kỳ", resultingRealm: "Luyện Khí Hậu Kỳ", pillId: "tu_tien:xd_danyao_dt", breakthrough: false },
  { currentRealm: "Luyện Khí Hậu Kỳ", resultingRealm: "Trúc Cơ Sơ Kỳ", pillId: "tu_tien:xd_danyao_zj", breakthrough: true },
  { currentRealm: "Trúc Cơ Sơ Kỳ", resultingRealm: "Trúc Cơ Trung Kỳ", pillId: "tu_tien:xd_danyao_xs", breakthrough: false },
  { currentRealm: "Trúc Cơ Trung Kỳ", resultingRealm: "Trúc Cơ Hậu Kỳ", pillId: "tu_tien:xd_danyao_hj", breakthrough: false },
  { currentRealm: "Trúc Cơ Hậu Kỳ", resultingRealm: "Kết Đan Sơ Kỳ", pillId: "tu_tien:xd_danyao_yz", breakthrough: true },
  { currentRealm: "Kết Đan Sơ Kỳ", resultingRealm: "Kết Đan Trung Kỳ", pillId: "tu_tien:xd_danyao_sm", breakthrough: false },
  { currentRealm: "Kết Đan Trung Kỳ", resultingRealm: "Kết Đan Hậu Kỳ", pillId: "tu_tien:xd_danyao_rl", breakthrough: false },
  { currentRealm: "Kết Đan Hậu Kỳ", resultingRealm: "Nguyên Anh Sơ Kỳ", pillId: "tu_tien:xd_danyao_jy", breakthrough: true },
  { currentRealm: "Nguyên Anh Sơ Kỳ", resultingRealm: "Nguyên Anh Trung Kỳ", pillId: "tu_tien:xd_danyao_yx", breakthrough: false },
  { currentRealm: "Nguyên Anh Trung Kỳ", resultingRealm: "Nguyên Anh Hậu Kỳ", pillId: "tu_tien:xd_danyao_ns", breakthrough: false },
  { currentRealm: "Nguyên Anh Hậu Kỳ", resultingRealm: "Hóa Thần Sơ Kỳ", pillId: "tu_tien:xd_danyao_hs", breakthrough: true },
  { currentRealm: "Hóa Thần Sơ Kỳ", resultingRealm: "Hóa Thần Trung Kỳ", pillId: "tu_tien:xd_danyao_hy", breakthrough: false },
  { currentRealm: "Hóa Thần Trung Kỳ", resultingRealm: "Hóa Thần Hậu Kỳ", pillId: "tu_tien:xd_danyao_hl", breakthrough: false },
  { currentRealm: "Hóa Thần Hậu Kỳ", resultingRealm: "Phản Hư Sơ Kỳ", pillId: "tu_tien:xd_danyao_kx", breakthrough: true },
];

export function buildCultivationStages(
  items: readonly ItemListEntry[],
): readonly CultivationStage[] {
  const itemsById = new Map(items.map((item) => [item.id, item] as const));

  return cultivationStageDefinitions.map((definition, index) => {
    const pill = itemsById.get(definition.pillId);
    if (!pill) {
      throw new Error(`Missing cultivation pill ${definition.pillId}`);
    }

    if (!pill.recipe) {
      throw new Error(`Cultivation pill ${definition.pillId} is missing a recipe`);
    }

    for (const ingredient of pill.recipe.ingredients) {
      if (!itemsById.has(ingredient.id)) {
        throw new Error(
          `Recipe ingredient ${ingredient.id} for cultivation pill ${definition.pillId} is missing from the catalog`,
        );
      }
    }

    return {
      ...definition,
      rank: index + 1,
      pill,
      recipe: pill.recipe,
    };
  });
}
