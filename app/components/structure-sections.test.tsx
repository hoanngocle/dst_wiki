import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ItemListEntry, StructureDetails } from "@/app/lib/item-catalog";
import { StructureSections } from "./structure-sections";

const evidence = [{ source: "public/data/catalog.json", locator: "fixture" }];
const craftedItem: ItemListEntry = {
  id: "base_game:axe",
  prefabId: "axe",
  namespace: "base_game",
  category: "item",
  name: "Rìu",
  englishName: "Axe",
  description: null,
  craftingNote: null,
  sprite: null,
  recipe: null,
  wiki: null,
};
const details: StructureDetails = {
  origin: {
    status: "known",
    naturallySpawned: false,
    renewable: true,
    spawnCode: "researchlab",
    sources: ["Chế tạo trong tab Khoa học"],
    respawn: null,
    craftable: true,
    note: null,
    evidence,
  },
  construction: {
    status: "known",
    outputCount: 1,
    ingredients: [
      { id: "base_game:goldnugget", name: "Vàng", amount: 1, sprite: null },
    ],
    tech: "TECH.NONE",
    station: null,
    restrictions: {},
    note: "Xây trực tiếp.",
    evidence,
  },
  functions: {
    status: "known",
    facts: [
      {
        key: "prototyper",
        label: "Mở khóa chế tạo",
        value: "Khoa học cấp 1",
        unit: null,
        context: "Đứng gần công trình",
        related: [],
        evidence,
      },
    ],
    reason: null,
    evidence,
  },
  craftables: {
    status: "known",
    recipes: [
      {
        result: { id: craftedItem.id, name: craftedItem.name, sprite: null },
        resultAmount: 1,
        ingredients: [
          { id: "base_game:goldnugget", name: "Vàng", amount: 1, sprite: null },
        ],
        station: "base_game:researchlab",
        tech: "TECH.SCIENCE_ONE",
        restrictions: {},
        note: null,
        evidence,
      },
    ],
    reason: null,
    evidence,
  },
  destruction: {
    status: "known",
    destroyable: true,
    tool: "Búa",
    work: "4",
    health: null,
    burnable: true,
    drops: [],
    regeneration: null,
    evidence,
  },
  visual: {
    status: "known",
    kind: "wiki_image",
    sprite: null,
    image: {
      title: "Science Machine.png",
      src: "/assets/wiki/researchlab.png",
      mime: "image/png",
      width: 128,
      height: 128,
      evidence,
    },
    alternatives: [],
    reason: null,
    evidence,
  },
};
const structure: ItemListEntry = {
  id: "base_game:researchlab",
  prefabId: "researchlab",
  namespace: "base_game",
  category: "structure",
  name: "Máy Khoa Học",
  englishName: "Science Machine",
  description: null,
  craftingNote: null,
  sprite: null,
  recipe: null,
  structureDetails: details,
  wiki: null,
};

describe("StructureSections", () => {
  it("renders all normalized structure sections and selects crafted items", () => {
    const onSelectItem = vi.fn();
    render(
      <StructureSections
        item={structure}
        itemsById={new Map([[craftedItem.id, craftedItem]])}
        onSelectItem={onSelectItem}
        titleId="structure"
      />,
    );

    for (const heading of [
      "Xuất hiện",
      "Công thức xây dựng",
      "Công dụng",
      "Vật phẩm chế tạo tại công trình",
      "Phá huỷ và thu hồi",
      "Hình ảnh",
    ]) {
      expect(screen.getByRole("heading", { name: heading })).toBeDefined();
    }
    expect(screen.getByText("Khoa học cấp 1")).toBeDefined();
    expect(screen.getByText("Chế tạo trong tab Khoa học")).toBeDefined();
    expect(screen.getByAltText("Science Machine.png")).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: "Rìu" }));
    expect(onSelectItem).toHaveBeenCalledWith(craftedItem);
  });

  it("notes naturally spawned, non-craftable structures without inventing a recipe", () => {
    const natural: ItemListEntry = {
      ...structure,
      id: "base_game:atrium_statue",
      prefabId: "atrium_statue",
      name: "Tượng cổ",
      structureDetails: {
        ...details,
        origin: {
          ...details.origin,
          naturallySpawned: true,
          craftable: false,
          note: "Công trình tự sinh trong thế giới và không thể chế tạo.",
        },
        construction: {
          ...details.construction,
          status: "none",
          outputCount: null,
          ingredients: [],
          tech: null,
          note: "Không thể chế tạo.",
        },
        craftables: {
          ...details.craftables,
          status: "none",
          recipes: [],
        },
      },
    };

    render(
      <StructureSections
        item={natural}
        itemsById={new Map()}
        onSelectItem={() => undefined}
        titleId="natural"
      />,
    );

    expect(
      screen.getByText("Công trình tự sinh trong thế giới và không thể chế tạo."),
    ).toBeDefined();
    expect(screen.getByText("Không thể chế tạo.")).toBeDefined();
    expect(screen.queryByLabelText("Nguyên liệu chế tạo")).toBeNull();
  });
});
