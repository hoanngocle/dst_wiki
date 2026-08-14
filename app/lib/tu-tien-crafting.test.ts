import { describe, expect, it } from "vitest";

import type { CatalogMobDetails, ItemListEntry, StructureDetails } from "./item-catalog";
import { selectHanLapCraftables } from "./tu-tien-crafting";

function item(
  id: string,
  name: string,
  overrides: Partial<ItemListEntry> = {},
): ItemListEntry {
  return {
    id,
    prefabId: id.split(":")[1] ?? id,
    namespace: "tu_tien",
    category: "item",
    name,
    englishName: null,
    description: null,
    craftingNote: null,
    sprite: null,
    recipe: {
      outputCount: 1,
      ingredients: [
        { id: "base_game:rock", name: "Đá", amount: 1, sprite: null },
      ],
    },
    details: {
      recipeStatus: "known",
      usage: { status: "unknown", recipes: [], effects: [] },
      dropBy: { status: "unknown", sources: [] },
    },
    wiki: null,
    ...overrides,
  };
}

const ingredient = item("base_game:rock", "Đá", {
  namespace: "base_game",
  recipe: null,
  details: null,
});

function structureWithKnownFunctions(): StructureDetails {
  return {
    origin: { status: "none", naturallySpawned: false, renewable: null, spawnCode: null, sources: [], respawn: null, craftable: true, note: null, evidence: [] },
    construction: { status: "none", outputCount: null, ingredients: [], tech: null, station: null, restrictions: {}, note: null, evidence: [] },
    functions: {
      status: "known",
      facts: [
        {
          key: "trader_enabled",
          label: "Có thể nhận vật phẩm",
          value: "true",
          unit: "boolean",
          context: null,
          related: [],
          evidence: [],
        },
      ],
      reason: null,
      evidence: [],
    },
    craftables: { status: "none", recipes: [], reason: null, evidence: [] },
    destruction: { status: "none", destroyable: null, tool: null, work: null, health: null, burnable: null, drops: [], regeneration: null, evidence: [] },
    visual: { status: "none", kind: null, sprite: null, image: null, alternatives: [], reason: null, evidence: [] },
  };
}

function mobWithDocumentedMechanics(): CatalogMobDetails {
  return {
    contract: "catalog",
    appearance: { status: "none", sources: [], spawnCodes: [], renewable: null, respawn: null, wikiUrl: null, evidence: [] },
    variants: [],
    stats: [],
    mechanics: [{ text: "Đã xác minh", sourceVariant: "manual", evidence: [] }],
    lootStatus: "none",
    loot: [],
  };
}

const catalog = {
  entities: [
    {
      key: "tu_tien:public_zeta",
      recipes: [{ restrictions: { builder_tags: [] } }],
    },
    {
      key: "tu_tien:han_lap_alpha",
      recipes: [{ restrictions: { builder_tags: ["player"] } }],
    },
    {
      key: "tu_tien:han_lap_xd",
      recipes: [{ restrictions: { builder_tags: ["xd_hantianzun"] } }],
    },
    {
      key: "tu_tien:other_character",
      recipes: [{ restrictions: { builder_tags: ["xd_luoshen"] } }],
    },
    {
      key: "tu_tien:manual_beta",
      recipes: [],
    },
    {
      key: "tu_tien:no_verified_use",
      recipes: [],
    },
  ],
};

describe("selectHanLapCraftables", () => {
  it("selects public, Han Lap, and verified manual recipes in deterministic order", () => {
    const publicRecipe = item("tu_tien:public_zeta", "Zeta", {
      details: {
        recipeStatus: "known",
        usage: {
          status: "known",
          recipes: [],
          effects: [{ trigger: "equip", text: "Đã xác minh", evidence: [] }],
        },
        dropBy: { status: "unknown", sources: [] },
      },
    });
    const hanLapRecipe = item("tu_tien:han_lap_alpha", "Alpha", {
      category: "pill",
      structureDetails: structureWithKnownFunctions(),
    });
    const manualAlchemyRecipe = item("tu_tien:manual_beta", "Beta", {
      mob: mobWithDocumentedMechanics(),
    });
    const hanTianZunRecipe = item("tu_tien:han_lap_xd", "Linh", {
      category: "pill",
      structureDetails: structureWithKnownFunctions(),
    });

    const selection = selectHanLapCraftables(
      [publicRecipe, hanLapRecipe, manualAlchemyRecipe, hanTianZunRecipe, ingredient],
      catalog,
    );

    expect(selection.items.map(({ id }) => id)).toEqual([
      "tu_tien:manual_beta",
      "tu_tien:public_zeta",
      "tu_tien:han_lap_alpha",
      "tu_tien:han_lap_xd",
    ]);
    expect(selection.excluded).toEqual([]);
  });

  it("accepts an item referenced by another resolved recipe as a verified use", () => {
    const material = item("tu_tien:material", "Nguyên liệu");
    const product = item("tu_tien:product", "Sản phẩm", {
      recipe: {
        outputCount: 1,
        ingredients: [
          { id: "tu_tien:material", name: "Nguyên liệu", amount: 1, sprite: null },
        ],
      },
    });

    const selection = selectHanLapCraftables(
      [material, product, ingredient],
      {
        entities: [
          { key: material.id, recipes: [] },
          { key: product.id, recipes: [] },
        ],
      },
    );

    expect(selection.items.map(({ id }) => id)).toEqual(["tu_tien:material"]);
    expect(selection.excluded).toEqual([
      { id: "tu_tien:product", reason: "no_verified_use" },
    ]);
  });

  it("excludes each rejected Tu Tiên item with a stable audit reason", () => {
    const otherCharacter = item("tu_tien:other_character", "Khác", {
      details: {
        recipeStatus: "known",
        usage: { status: "known", recipes: [], effects: [] },
        dropBy: { status: "unknown", sources: [] },
      },
    });
    const noRecipe = item("tu_tien:no_recipe", "Không có công thức", {
      recipe: null,
    });
    const noVerifiedUse = item("tu_tien:no_verified_use", "Chưa xác minh");
    const unresolvedIngredient = item("tu_tien:unresolved", "Thiếu nguyên liệu", {
      recipe: {
        outputCount: 1,
        ingredients: [
          { id: "tu_tien:missing", name: "Thiếu", amount: 1, sprite: null },
        ],
      },
      details: {
        recipeStatus: "known",
        usage: { status: "known", recipes: [], effects: [] },
        dropBy: { status: "unknown", sources: [] },
      },
    });

    const selection = selectHanLapCraftables(
      [otherCharacter, noRecipe, noVerifiedUse, unresolvedIngredient, ingredient],
      catalog,
    );

    expect(selection.items).toEqual([]);
    expect(selection.excluded).toEqual([
      { id: "tu_tien:other_character", reason: "other_character" },
      { id: "tu_tien:no_recipe", reason: "no_recipe" },
      { id: "tu_tien:no_verified_use", reason: "no_verified_use" },
      { id: "tu_tien:unresolved", reason: "unresolved_ingredient" },
    ]);
  });

  it("requires concrete usage or structure evidence instead of a known label", () => {
    const emptyKnownUsage = item("tu_tien:empty_usage", "Usage rỗng", {
      details: {
        recipeStatus: "known",
        usage: { status: "known", recipes: [], effects: [] },
        dropBy: { status: "unknown", sources: [] },
      },
    });
    const emptyKnownFunctions = item("tu_tien:empty_functions", "Function rỗng", {
      structureDetails: {
        ...structureWithKnownFunctions(),
        functions: { status: "known", facts: [], reason: null, evidence: [] },
      },
    });

    const selection = selectHanLapCraftables(
      [emptyKnownUsage, emptyKnownFunctions, ingredient],
      {
        entities: [
          { key: emptyKnownUsage.id, recipes: [] },
          { key: emptyKnownFunctions.id, recipes: [] },
        ],
      },
    );

    expect(selection.items).toEqual([]);
    expect(selection.excluded).toEqual([
      { id: emptyKnownUsage.id, reason: "no_verified_use" },
      { id: emptyKnownFunctions.id, reason: "no_verified_use" },
    ]);
  });

  it.each([
    ["top-level entities", { entities: {} }, /catalog.*entities/i],
    ["entity", { entities: [null] }, /entities\[0\]/i],
    [
      "entity key",
      { entities: [{ key: 42, recipes: [] }] },
      /entities\[0\]\.key/i,
    ],
    [
      "entity recipes",
      { entities: [{ key: "tu_tien:manual", recipes: null }] },
      /entities\[0\]\.recipes/i,
    ],
    [
      "recipe record",
      { entities: [{ key: "tu_tien:manual", recipes: [null] }] },
      /entities\[0\]\.recipes\[0\]/i,
    ],
    [
      "recipe restrictions",
      {
        entities: [
          { key: "tu_tien:manual", recipes: [{ restrictions: "public" }] },
        ],
      },
      /restrictions/i,
    ],
    [
      "builder tags",
      {
        entities: [
          {
            key: "tu_tien:manual",
            recipes: [{ restrictions: { builder_tags: ["player", 42] } }],
          },
        ],
      },
      /builder_tags/i,
    ],
  ])("throws when the catalog has malformed %s", (_label, payload, message) => {
    expect(() => selectHanLapCraftables([], payload)).toThrow(message);
  });

  it("throws when a craftable has no matching catalog entity", () => {
    const manualRecipe = item("tu_tien:missing_entity", "Thiếu entity", {
      mob: mobWithDocumentedMechanics(),
    });

    expect(() =>
      selectHanLapCraftables([manualRecipe, ingredient], { entities: [] }),
    ).toThrow(/missing catalog entity.*tu_tien:missing_entity/i);
  });
});
