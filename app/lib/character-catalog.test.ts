import { describe, expect, it } from "vitest";

import characterGuidesPayload from "../../data/manual/character-guides.json";
import characterProfilesPayload from "../../data/manual/character-profiles.json";
import { parseItemPayload, type ItemListEntry } from "./item-catalog";
import {
  buildCharacterCatalog,
  filterCharacters,
  parseCharacterGuides,
  parseCharacterProfiles,
  selectCharacters,
} from "./character-catalog";

function createItem(
  id: string,
  category: ItemListEntry["category"] = "character",
  name = id,
): ItemListEntry {
  return {
    id,
    prefabId: id.split(":")[1],
    namespace: id.startsWith("tu_tien:") ? "tu_tien" : "base_game",
    category,
    name,
    englishName: name,
    description: null,
    craftingNote: null,
    sprite: {
      src: `/assets/game/${id.replace(":", "-")}.png`,
      uv: { u1: 0, u2: 1, v1: 0, v2: 1 },
    },
    recipe: null,
    wiki: null,
  };
}

function profile(
  namespace: "base_game" | "tu_tien",
  portrait: string,
  name: { vi: string; en: string },
) {
  return {
    namespace,
    name,
    title: { vi: "Danh hiệu", en: "Title" },
    description: { vi: "Mô tả", en: "Description" },
    portrait: { path: portrait, sourceUrl: "https://example.com/source" },
    stats: {
      health: { value: 150 },
      hunger: { value: 150 },
      sanity: { value: 200 },
    },
    abilities: [
      {
        name: { vi: "Kiếm pháp", en: "Sword Art" },
        effect: { vi: "Gây sát thương.", en: "Deals damage." },
      },
    ],
    startingItems: [
      {
        code: "starter",
        name: { vi: "Vật phẩm nguồn", en: "Source Item" },
        quantity: 1,
        effect: { vi: "Khởi đầu.", en: "Starting equipment." },
      },
    ],
    artifacts: [
      {
        code: "artifact_blade",
        name: { vi: "Pháp bảo nguồn", en: "Source Artifact" },
        effect: { vi: "Tăng sức mạnh.", en: "Increases power." },
      },
    ],
    sourceVersion: "1.0.0",
  };
}

function profilesPayload() {
  return {
    schemaVersion: 1,
    profiles: {
      xd_hantianzun: profile(
        "tu_tien",
        "/assets/dst/characters/xd_hantianzun.png",
        { vi: "Hàn Thiên Tôn", en: "Cold Sky Venerable" },
      ),
      wilson: profile(
        "base_game",
        "/assets/dst/characters/base/wilson.png",
        { vi: "Wilson", en: "Wilson" },
      ),
    },
  };
}

function payloadWithDuplicate(identity: "base:wilson") {
  const code = identity.split(":")[1];
  return {
    schemaVersion: 1,
    profiles: {
      [code]: profile(
        "base_game",
        "/assets/dst/characters/base/wilson.png",
        { vi: "Wilson", en: "Wilson" },
      ),
      [code.toUpperCase()]: profile(
        "base_game",
        "/assets/dst/characters/base/wilson.png",
        { vi: "Wilson", en: "Wilson" },
      ),
    },
  };
}

function guidesPayload() {
  return {
    schemaVersion: 1,
    guides: {
      xd_hantianzun: {
        roles: ["Cận chiến"],
        attackPattern: "Áp sát rồi tung kiếm.",
        range: "melee",
        complexity: "advanced",
        summary: "Một kiếm tu thiên về áp sát.",
        strengths: ["Sát thương cao."],
        tradeoffs: ["Cần giữ khoảng cách hợp lý."],
        firstSteps: ["Trang bị kiếm."],
        combat: [
          {
            label: "Kiếm quyết",
            description: "Tấn công mục tiêu.",
            confidence: "confirmed",
            evidence: ["private:combat"],
          },
        ],
        realmMilestones: [
          {
            realm: "Trúc Cơ",
            unlocks: [
              {
                label: "Kiếm khí",
                description: "Mở khóa kiếm khí.",
                confidence: "confirmed",
                evidence: ["private:realm"],
              },
            ],
          },
        ],
        artifacts: [
          {
            label: "Thần kiếm",
            description: "Pháp bảo chiến đấu.",
            confidence: "confirmed",
            evidence: ["private:artifact"],
          },
        ],
        sourceVersion: "1.0.0",
      },
    },
  };
}

const items = [
  createItem("base_game:wilson", "character", "Wilson"),
  createItem("tu_tien:xd_hantianzun", "character", "Hàn Thiên Tôn"),
  createItem("tu_tien:starter", "item", "Khởi Nguyên Kiếm"),
  createItem("tu_tien:artifact_blade", "item", "Thiên Đạo Kiếm"),
];

describe("character source contracts", () => {
  it("parses all transferred curated character sources", () => {
    const profiles = parseCharacterProfiles(characterProfilesPayload);
    const guides = parseCharacterGuides(characterGuidesPayload);

    expect(profiles).toHaveLength(28);
    expect(guides).toHaveLength(9);
    expect(JSON.stringify([...guides.values()])).not.toContain("evidence");
    expect(buildCharacterCatalog(items, profiles, guides, "vi")).toHaveLength(28);
  });

  it("rejects unsupported profile and guide schema versions", () => {
    expect(() => parseCharacterProfiles({ ...profilesPayload(), schemaVersion: 2 }))
      .toThrow(/schema version 1/i);
    expect(() => parseCharacterGuides({ ...guidesPayload(), schemaVersion: 2 }))
      .toThrow(/schema version 1/i);
  });

  it("rejects malformed profile and guide records", () => {
    expect(() =>
      parseCharacterProfiles({ schemaVersion: 1, profiles: { wilson: null } }),
    ).toThrow(/profile.*object/i);
    expect(() =>
      parseCharacterGuides({ schemaVersion: 1, guides: { xd_hantianzun: null } }),
    ).toThrow(/guide.*object/i);
  });

  it("rejects duplicate character identities", () => {
    expect(() => parseCharacterProfiles(payloadWithDuplicate("base:wilson")))
      .toThrow(/duplicate character identity/i);
  });

  it("rejects duplicate guide identities", () => {
    const guide = guidesPayload().guides.xd_hantianzun;
    expect(() =>
      parseCharacterGuides({
        schemaVersion: 1,
        guides: { xd_hantianzun: guide, XD_HANTIANZUN: guide },
      }),
    ).toThrow(/duplicate guide identity/i);
  });

  it("rejects invalid character asset paths", () => {
    const payload = profilesPayload();
    payload.profiles.wilson.portrait.path = "../../private/wilson.png";

    expect(() => parseCharacterProfiles(payload)).toThrow(/portrait path/i);
  });

  it("rejects a portrait path that does not match its namespace and code", () => {
    const payload = profilesPayload();
    payload.profiles.wilson.portrait.path =
      "/assets/dst/characters/wilson.png";

    expect(() => parseCharacterProfiles(payload)).toThrow(/portrait path/i);
  });

  it("accepts a display-only stat when the numeric value is unavailable", () => {
    const source = profilesPayload();
    const payload: unknown = {
      ...source,
      profiles: {
        ...source.profiles,
        wilson: {
          ...source.profiles.wilson,
          stats: {
            ...source.profiles.wilson.stats,
            health: {
              value: null,
              display: "20–80 tuổi",
              note: "Thanh Tuổi thay cho Máu.",
            },
          },
        },
      },
    };

    expect(parseCharacterProfiles(payload).get("base_game:wilson")?.stats.health)
      .toMatchObject({ value: null, display: "20–80 tuổi" });
  });
});

describe("buildCharacterCatalog", () => {
  it("builds stable public details without evidence", () => {
    const profiles = parseCharacterProfiles(profilesPayload());
    const guides = parseCharacterGuides(guidesPayload());
    const characters = buildCharacterCatalog(items, profiles, guides, "vi");

    expect(characters[0].id).toBe("tu_tien:xd_hantianzun");
    expect(JSON.stringify(characters)).not.toContain("evidence");
    expect(characters[0].startingItems[0]).toMatchObject({
      code: expect.any(String),
      name: "Khởi Nguyên Kiếm",
      icon: items[2].sprite,
    });
    expect(characters[0].artifacts[0]).toMatchObject({
      code: "artifact_blade",
      name: "Thiên Đạo Kiếm",
      icon: items[3].sprite,
    });
  });

  it("falls back to English text when Vietnamese is empty", () => {
    const fallbackPayload = profilesPayload();
    fallbackPayload.profiles.wilson.name.vi = "";
    const fallbackProfiles = parseCharacterProfiles(fallbackPayload);

    expect(buildCharacterCatalog(items, fallbackProfiles, new Map(), "vi")[1].name)
      .toBe("Wilson");
  });

  it("uses the item catalog English equipment name for English output", () => {
    const englishItems = items.map((item) =>
      item.id === "tu_tien:starter"
        ? { ...item, englishName: "Origin Sword" }
        : item,
    );

    const character = buildCharacterCatalog(
      englishItems,
      parseCharacterProfiles(profilesPayload()),
      parseCharacterGuides(guidesPayload()),
      "en",
    )[0];

    expect(character.startingItems[0].name).toBe("Origin Sword");
  });

  it("orders Tu Tien characters before base-game characters deterministically", () => {
    const characters = buildCharacterCatalog(
      [...items].reverse(),
      parseCharacterProfiles(profilesPayload()),
      parseCharacterGuides(guidesPayload()),
      "vi",
    );

    expect(characters.map((character) => character.id)).toEqual([
      "tu_tien:xd_hantianzun",
      "base_game:wilson",
    ]);
  });
});

describe("published character compatibility", () => {
  it("normalizes curated bilingual profiles to the existing item-detail contract", () => {
    const parsed = parseItemPayload({
      schema_version: 7,
      items: [
        {
          id: "base_game:wilson",
          prefabId: "wilson",
          namespace: "base_game",
          category: "character",
          name: "Wilson",
          englishName: "Wilson",
          description: "A scientist.",
          craftingNote: null,
          sprite: null,
          recipe: null,
          details: null,
          mob: null,
          character: {
            title: { vi: "Nhà khoa học quý ông", en: "The Gentleman Scientist" },
            abilities: [
              {
                name: { vi: "Kiến thức", en: "Insight" },
                effect: { vi: "Mở khóa kỹ năng.", en: "Unlocks skills." },
              },
            ],
            portrait: { path: "/assets/dst/characters/base/wilson.png" },
            stats: {},
            startingItems: [],
            artifacts: [],
            guide: null,
          },
          structureDetails: null,
          wiki: null,
        },
      ],
    });

    expect(parsed[0].character).toEqual({
      title: "Nhà khoa học quý ông",
      survivability: null,
      quote: null,
      abilities: ["Kiến thức: Mở khóa kỹ năng."],
    });
  });
});

describe("character selectors", () => {
  const characters = buildCharacterCatalog(
    items,
    parseCharacterProfiles(profilesPayload()),
    parseCharacterGuides(guidesPayload()),
    "vi",
  );

  it("keeps playable characters from both DST and Tu Tien", () => {
    expect(selectCharacters(items).map((item) => item.id)).toEqual([
      "base_game:wilson",
      "tu_tien:xd_hantianzun",
    ]);
  });

  it("normalizes Vietnamese and English search text", () => {
    expect(filterCharacters(characters, { query: "han thien" })).toHaveLength(1);
    expect(filterCharacters(characters, { query: "cold sky" })).toHaveLength(1);
  });

  it("normalizes Vietnamese crossed d in search text", () => {
    const daji = { ...characters[0], name: "Đát Kỷ", englishName: "Daji" };

    expect(filterCharacters([daji], { query: "dat ky" })).toHaveLength(1);
  });

  it("filters by namespace", () => {
    expect(
      filterCharacters(characters, { namespace: "base_game" }).map(
        (character) => character.id,
      ),
    ).toEqual(["base_game:wilson"]);
  });
});
