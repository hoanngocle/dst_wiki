import { describe, expect, it } from "vitest";

import { parseItemPayload } from "./item-catalog";

const validPayload = {
  schema_version: 3,
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
    },
  ],
};

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
  });

  it("accepts special recipes with no normal ingredients", () => {
    const payload = structuredClone(validPayload);
    payload.items[0].recipe.ingredients = [];

    expect(parseItemPayload(payload)[0].recipe?.ingredients).toEqual([]);
  });

  it("rejects legacy payloads and invalid prefab categories", () => {
    expect(() =>
      parseItemPayload({ ...validPayload, schema_version: 2 }),
    ).toThrow(/schema version 3/i);

    const payload = structuredClone(validPayload) as unknown as {
      items: Array<{ category: string }>;
    };
    payload.items[0].category = "unknown-category";
    expect(() => parseItemPayload(payload)).toThrow(/category/i);
  });

  it("rejects non-integer ingredient quantities", () => {
    const payload = structuredClone(validPayload);
    payload.items[0].recipe.ingredients[0].amount = 1.5;

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
});
