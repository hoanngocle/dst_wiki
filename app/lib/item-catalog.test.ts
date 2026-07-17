import { describe, expect, it } from "vitest";

import { parseItemPayload } from "./item-catalog";

const validPayload = {
  schema_version: 6,
  items: [
    {
      id: "tu_tien:xd_sword",
      prefabId: "xd_sword",
      namespace: "tu_tien",
      category: "item",
      name: "Kiếm Thử",
      englishName: "Test Sword",
      description: "Một thanh kiếm",
      craftingNote: "Rèn một thanh kiếm thử",
      sprite: {
        src: "/assets/game/asset.png",
        uv: { u1: 0, u2: 1, v1: 0, v2: 1 },
      },
      recipe: {
        outputCount: 1,
        ingredients: [
          {
            id: "base_game:goldnugget",
            name: "Vàng",
            amount: 2,
            sprite: null,
          },
        ],
      },
      details: {
        recipeStatus: "known",
        usage: {
          status: "known",
          recipes: [
            {
              result: {
                id: "tu_tien:xd_pill",
                name: "Linh Đan",
                sprite: null,
              },
              resultAmount: 1,
              subjectAmount: 2,
              ingredients: [],
              craftingNote: "Yêu cầu người chế tạo xd_alchemist.",
            },
          ],
          effects: [
            {
              trigger: "equip",
              text: "Khi trang bị: tăng sát thương.",
              evidence: [
                {
                  source: "public/data/catalog.json",
                  locator: "tu_tien:xd_sword:stats",
                },
              ],
            },
          ],
        },
        dropBy: {
          status: "known",
          sources: [
            {
              type: "drop",
              source: {
                id: "tu_tien:xd_boss",
                name: "Yêu Vương",
                sprite: null,
              },
              quantity: "1",
              chance: "25%",
              conditions: null,
              evidence: [
                {
                  source: "public/data/catalog.json",
                  locator: "tu_tien:xd_sword:acquisition",
                },
              ],
            },
          ],
        },
      },
      structureDetails: null,
      wiki: null,
    },
  ],
};

function makeValidItem(
  prefabId: string,
  {
    namespace = "tu_tien",
    sprite = structuredClone(validPayload.items[0].sprite),
  }: {
    namespace?: "tu_tien" | "base_game";
    sprite?: (typeof validPayload.items)[number]["sprite"] | null;
  } = {},
) {
  return {
    ...structuredClone(validPayload.items[0]),
    id: `${namespace}:${prefabId}`,
    prefabId,
    namespace,
    sprite,
    details:
      namespace === "tu_tien"
        ? structuredClone(validPayload.items[0].details)
        : null,
  };
}

describe("parseItemPayload", () => {
  it("accepts the generated compact item contract", () => {
    const items = parseItemPayload(validPayload);

    expect(items).toHaveLength(1);
    expect(items[0].recipe?.ingredients[0]).toEqual({
      id: "base_game:goldnugget",
      name: "Vàng",
      amount: 2,
      sprite: null,
    });
    expect(items[0].craftingNote).toBe("Rèn một thanh kiếm thử");
    expect(items[0].details?.usage.effects[0].trigger).toBe("equip");
    expect(items[0].details?.dropBy.sources[0].chance).toBe("25%");
  });

  it("accepts special recipes with no normal ingredients", () => {
    const payload = structuredClone(validPayload);
    payload.items[0].recipe.ingredients = [];

    expect(parseItemPayload(payload)[0].recipe?.ingredients).toEqual([]);
  });

  it("accepts the pill category", () => {
    const payload = structuredClone(validPayload);
    payload.items[0].category = "pill";

    expect(parseItemPayload(payload)[0].category).toBe("pill");
  });

  it("accepts complete structure details and rejects them on non-structures", () => {
    const payload = structuredClone(validPayload);
    const structure = makeValidItem("researchlab", {
      namespace: "base_game",
    }) as unknown as Record<string, unknown>;
    structure.category = "structure";
    structure.structureDetails = {
      origin: {
        status: "known",
        naturallySpawned: false,
        renewable: true,
        spawnCode: "researchlab",
        sources: [],
        respawn: null,
        craftable: true,
        note: null,
        evidence: [{ source: "public/data/catalog.json", locator: "origin" }],
      },
      construction: {
        status: "known",
        outputCount: 1,
        ingredients: [],
        tech: "TECH.SCIENCE_ONE",
        station: null,
        restrictions: {},
        note: null,
        evidence: [{ source: "public/data/catalog.json", locator: "construction" }],
      },
      functions: {
        status: "known",
        facts: [
          {
            key: "prototyper",
            label: "Mở khóa chế tạo",
            value: "Science 1",
            unit: null,
            context: null,
            related: [],
            evidence: [{ source: "https://dontstarve.wiki.gg", locator: "revision:1" }],
          },
        ],
        reason: null,
        evidence: [{ source: "https://dontstarve.wiki.gg", locator: "revision:1" }],
      },
      craftables: {
        status: "none",
        recipes: [],
        reason: null,
        evidence: [{ source: "public/data/catalog.json", locator: "craftables" }],
      },
      destruction: {
        status: "known",
        destroyable: true,
        tool: "Hammer",
        work: "4",
        health: null,
        burnable: true,
        drops: [],
        regeneration: null,
        evidence: [{ source: "https://dontstarve.wiki.gg", locator: "revision:1" }],
      },
      visual: {
        status: "known",
        kind: "inventory_icon",
        sprite: structuredClone(validPayload.items[0].sprite),
        image: null,
        alternatives: [],
        reason: null,
        evidence: [{ source: "public/data/catalog.json", locator: "visual" }],
      },
    };
    payload.items = [structure] as unknown as typeof payload.items;

    const parsed = parseItemPayload(payload)[0];
    expect(parsed.structureDetails?.construction.tech).toBe("TECH.SCIENCE_ONE");
    expect(parsed.structureDetails?.functions.facts[0].label).toBe(
      "Mở khóa chế tạo",
    );

    const nonStructure = structuredClone(validPayload);
    (nonStructure.items[0] as unknown as Record<string, unknown>).structureDetails =
      structure.structureDetails;
    expect(() => parseItemPayload(nonStructure)).toThrow(/non-structure.*structureDetails/i);
  });

  it("rejects legacy payloads and invalid prefab categories", () => {
    expect(() =>
      parseItemPayload({ ...validPayload, schema_version: 4 }),
    ).toThrow(/schema version 6/i);

    const payload = structuredClone(validPayload) as unknown as {
      items: Array<{ category: string }>;
    };
    payload.items[0].category = "unknown-category";
    expect(() => parseItemPayload(payload)).toThrow(/category/i);
  });

  it("accepts positive fractional ingredient quantities", () => {
    const payload = structuredClone(validPayload);
    payload.items[0].recipe.ingredients[0].amount = 1.5;

    expect(parseItemPayload(payload)[0].recipe?.ingredients[0].amount).toBe(1.5);
  });

  it("rejects non-positive ingredient quantities", () => {
    const payload = structuredClone(validPayload);
    payload.items[0].recipe.ingredients[0].amount = 0;

    expect(() => parseItemPayload(payload)).toThrow(/ingredient amount/i);
  });

  it("rejects malformed sprite coordinates", () => {
    const payload = structuredClone(validPayload) as unknown as {
      items: Array<{ sprite: { uv: { u2: unknown } } }>;
    };
    payload.items[0].sprite.uv.u2 = "1";

    expect(() => parseItemPayload(payload)).toThrow(/sprite/i);
  });

  it("rejects a missing crafting note field", () => {
    const payload = structuredClone(validPayload) as unknown as {
      items: Array<{ craftingNote?: string | null }>;
    };
    delete payload.items[0].craftingNote;

    expect(() => parseItemPayload(payload)).toThrow(/craftingNote/i);
  });

  it("requires details for Tu Tiên items and null details for base-game items", () => {
    const missing = structuredClone(validPayload) as unknown as {
      items: Array<{ details: unknown }>;
    };
    missing.items[0].details = null;
    expect(() => parseItemPayload(missing)).toThrow(/Tu Tiên.*details/i);

    const baseGame = {
      schema_version: 6,
      items: [makeValidItem("goldnugget", { namespace: "base_game" })],
    } as unknown as { schema_version: number; items: Array<{ details: unknown }> };
    baseGame.items[0].details = structuredClone(validPayload.items[0].details);
    expect(() => parseItemPayload(baseGame)).toThrow(/base-game.*details/i);
  });

  it("rejects known empty sections and invalid drop source types", () => {
    const emptyUsage = structuredClone(validPayload);
    emptyUsage.items[0].details.usage = {
      status: "known",
      recipes: [],
      effects: [],
    };
    expect(() => parseItemPayload(emptyUsage)).toThrow(/known usage.*data/i);

    const invalidDrop = structuredClone(validPayload) as unknown as {
      items: Array<{ details: { dropBy: { sources: Array<{ type: string }> } } }>;
    };
    invalidDrop.items[0].details.dropBy.sources[0].type = "spawn";
    expect(() => parseItemPayload(invalidDrop)).toThrow(/drop source type/i);
  });

  it("accepts complete wiki metadata and related pages", () => {
    const payload = structuredClone(validPayload) as unknown as {
      schema_version: number;
      items: Array<Record<string, unknown>>;
    };
    payload.items[0].wiki = {
      pageId: 158,
      title: "Fish Morsel",
      canonicalUrl: "https://dontstarve.wiki.gg/wiki/Fish_Morsel",
      categories: ["Food", "Fishes"],
      mappingState: "mapped",
      detailUrl: "/data/wiki/pages/158.json",
      relatedPages: [
        {
          pageId: 159,
          title: "Fish Morsel/DST",
          canonicalUrl: "https://dontstarve.wiki.gg/wiki/Fish_Morsel/DST",
          detailUrl: "/data/wiki/pages/159.json",
        },
      ],
    };

    const wiki = parseItemPayload(payload)[0].wiki;

    expect(wiki?.pageId).toBe(158);
    expect(wiki?.relatedPages[0].title).toBe("Fish Morsel/DST");
  });

  it("removes effect-only prefabs while preserving retained order", () => {
    const payload = {
      schema_version: 6,
      items: [
        makeValidItem("first"),
        makeValidItem("spark_fx"),
        makeValidItem("last"),
      ],
    };

    expect(parseItemPayload(payload).map((item) => item.prefabId)).toEqual([
      "first",
      "last",
    ]);
  });

  it("prefers a pictured _item counterpart without crossing namespaces", () => {
    const payload = {
      schema_version: 6,
      items: [
        makeValidItem("gate"),
        makeValidItem("gate", { namespace: "base_game" }),
        makeValidItem("gate_item"),
        makeValidItem("standalone_item", { sprite: null }),
      ],
    };

    expect(
      parseItemPayload(payload).map((item) => `${item.namespace}:${item.prefabId}`),
    ).toEqual([
      "base_game:gate",
      "tu_tien:gate_item",
      "tu_tien:standalone_item",
    ]);
  });

  it("keeps the base prefab when its _item counterpart has no image", () => {
    const payload = {
      schema_version: 6,
      items: [makeValidItem("gate"), makeValidItem("gate_item", { sprite: null })],
    };

    expect(parseItemPayload(payload).map((item) => item.prefabId)).toEqual(["gate"]);
  });
});
