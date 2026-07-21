import { describe, expect, it } from "vitest";

import { parseItemPayload } from "./item-catalog";

const validPayload = {
  schema_version: 7,
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

const animalEvidence = [
  { source: "fandom", locator: "revision:67890" },
];

function makeAnimalMob() {
  return {
    identity: {
      primaryCode: "koalefant_summer",
      prefabCodes: ["koalefant_summer", "koalefant_winter"],
      sourcePageId: 12345,
      sourceUrl: "https://dontstarve.fandom.com/wiki/Koalefant",
      revisionId: 67890,
    },
    classification: { type: "mob", tags: ["Animals"], game: "DST" },
    variants: [
      { code: "koalefant_summer", label: "Summer Koalefant", order: 0, sprite: null },
      { code: "koalefant_winter", label: "Winter Koalefant", order: 1, sprite: null },
    ],
    stats: {
      status: "known",
      values: [
        {
          key: "max_health",
          label: "Health",
          value: 1000,
          unit: "hp",
          sourceVariant: "koalefant_summer",
          evidence: animalEvidence,
        },
      ],
      reason: null,
      evidence: animalEvidence,
    },
    effects: { status: "none", values: [], reason: "source_has_no_values", evidence: animalEvidence },
    combat: {
      status: "known",
      values: [
        {
          key: "attack_damage",
          label: "Damage",
          value: 50,
          unit: null,
          sourceVariant: "koalefant_summer",
          evidence: animalEvidence,
        },
      ],
      reason: null,
      evidence: animalEvidence,
    },
    movement: { status: "unknown", values: [], reason: "not_verified", evidence: animalEvidence },
    traits: {
      status: "known",
      values: [{ text: "Leaves a suspicious dirt pile.", sourceVariant: null }],
      reason: null,
      evidence: animalEvidence,
    },
    loot: {
      status: "known",
      values: [
        {
          item: { id: "base_game:meat", name: "Meat", sprite: null },
          quantity: "×8",
          chance: null,
          conditions: null,
          method: "kill",
          sourceVariant: "koalefant_summer",
          game: "DST",
        },
      ],
      reason: null,
      evidence: animalEvidence,
    },
    spawnsFrom: { status: "none", values: [], reason: "source_has_no_values", evidence: animalEvidence },
    notes: {
      status: "known",
      values: [
        {
          source: "Koalefants leave suspicious dirt piles.",
          summaryVi: "Koalefant để lại đống đất khả nghi.",
          sourceSha256: "a".repeat(64),
          status: "reviewed",
        },
      ],
      reason: null,
      evidence: animalEvidence,
    },
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

  it("accepts phase-aware Mob and Boss details", () => {
    const boss = makeValidItem("alterguardian_phase3", {
      namespace: "base_game",
    }) as unknown as Record<string, unknown>;
    boss.category = "boss";
    boss.mob = {
      appearance: {
        status: "known",
        sources: ["Được triệu hồi tại Mysterious Energy"],
        spawnCodes: ["alterguardian_phase3", "alterguardian_phase3dead"],
        renewable: null,
        respawn: null,
        wikiUrl: "https://dontstarve.wiki.gg/wiki/Celestial_Champion",
        evidence: [{ source: "wiki", locator: "Celestial Champion" }],
      },
      variants: [
        {
          id: "base_game:alterguardian_phase3",
          prefabId: "alterguardian_phase3",
          name: "Celestial Champion",
          role: "phase",
          order: 3,
          sprite: null,
        },
        {
          id: "base_game:alterguardian_phase3dead",
          prefabId: "alterguardian_phase3dead",
          name: "Defeated Celestial Champion",
          role: "post_defeat",
          order: 4,
          sprite: null,
        },
      ],
      stats: [
        {
          key: "max_health",
          label: "Máu tối đa",
          value: 14000,
          unit: "hp",
          sourceVariant: "base_game:alterguardian_phase3",
          evidence: [{ source: "catalog", locator: "max_health" }],
        },
      ],
      mechanics: [
        {
          text: "Trạng thái đặc biệt: summon, spin",
          sourceVariant: "base_game:alterguardian_phase3",
          evidence: [{ source: "catalog", locator: "special_states" }],
        },
      ],
      lootStatus: "known",
      loot: [
        {
          item: {
            id: "base_game:alterguardianhat",
            name: "Enlightened Crown",
            sprite: null,
          },
          minimum: 1,
          maximum: 1,
          chance: "100%",
          method: "mine_post_defeat",
          sourceVariant: "base_game:alterguardian_phase3dead",
          lootTable: "alterguardian_phase3dead",
          conditions: "Bảng rơi: alterguardian_phase3dead",
          evidence: [{ source: "scripts.zip", locator: "alterguardian_phase3dead" }],
        },
      ],
    };

    const parsed = parseItemPayload({ schema_version: 7, items: [boss] })[0];

    expect(parsed.mob?.contract).toBe("catalog");
    if (parsed.mob?.contract !== "catalog") {
      throw new Error("expected catalog Mob contract");
    }

    expect(parsed.mob.appearance.sources[0]).toContain("Mysterious Energy");
    expect(parsed.mob.variants[1].role).toBe("post_defeat");
    expect(parsed.mob.stats[0].sourceVariant).toBe(
      "base_game:alterguardian_phase3",
    );
    expect(parsed.mob.loot[0]).toMatchObject({
      minimum: 1,
      maximum: 1,
      method: "mine_post_defeat",
      sourceVariant: "base_game:alterguardian_phase3dead",
    });
  });

  it("accepts the expanded DST Animals Mob contract", () => {
    const animal = makeValidItem("koalefant_summer", {
      namespace: "base_game",
    }) as unknown as Record<string, unknown>;
    animal.category = "mob";
    animal.mob = makeAnimalMob();

    const mob = parseItemPayload({ schema_version: 7, items: [animal] })[0].mob as
      | ReturnType<typeof makeAnimalMob>
      | null;

    expect(mob?.identity.prefabCodes).toEqual([
      "koalefant_summer",
      "koalefant_winter",
    ]);
    expect(mob?.combat.values[0]).toMatchObject({
      key: "attack_damage",
      value: 50,
    });
    expect(mob?.notes.values[0]).toMatchObject({ status: "reviewed" });
  });

  it("rejects known empty Animals sections, duplicate codes, and non-DST classification", () => {
    const payloadFor = (mob: ReturnType<typeof makeAnimalMob>) => {
      const animal = makeValidItem("koalefant_summer", {
        namespace: "base_game",
      }) as unknown as Record<string, unknown>;
      animal.category = "mob";
      animal.mob = mob;
      return { schema_version: 7, items: [animal] };
    };

    const knownEmpty = makeAnimalMob();
    knownEmpty.combat = {
      status: "known",
      values: [],
      reason: null,
      evidence: animalEvidence,
    };
    expect(() => parseItemPayload(payloadFor(knownEmpty))).toThrow(/known combat/i);

    const duplicateCodes = makeAnimalMob();
    duplicateCodes.identity.prefabCodes = [
      "koalefant_summer",
      "koalefant_summer",
    ];
    expect(() => parseItemPayload(payloadFor(duplicateCodes))).toThrow(/prefabCodes/i);

    const nonDst = makeAnimalMob();
    nonDst.classification = {
      type: "mob",
      tags: ["Animals"],
      game: "Shipwrecked",
    } as unknown as typeof nonDst.classification;
    expect(() => parseItemPayload(payloadFor(nonDst))).toThrow(/DST/i);
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
    ).toThrow(/schema version 7/i);

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
      schema_version: 7,
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
      schema_version: 7,
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
      schema_version: 7,
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
      schema_version: 7,
      items: [makeValidItem("gate"), makeValidItem("gate_item", { sprite: null })],
    };

    expect(parseItemPayload(payload).map((item) => item.prefabId)).toEqual(["gate"]);
  });
});
