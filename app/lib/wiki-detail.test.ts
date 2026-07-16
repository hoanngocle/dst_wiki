import { describe, expect, it } from "vitest";

import { parseWikiPageDetail } from "./wiki-detail";

const validDetail = {
  schema_version: 1,
  pageId: 100736,
  title: "Halberd",
  canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd",
  html: "<p>Pointy and hurty.</p>",
  categories: ["Items", "Weapons"],
  images: [
    {
      title: "File:Halberd.png",
      src: "/assets/wiki/halberd.png",
      mime: "image/png",
      width: 64,
      height: 64,
    },
  ],
  recipes: [],
  revision: {
    id: 569319,
    sha1: "5bf67f6c77b1a0d0c5bb66b0ef02ccf5c04dba64",
    timestamp: "2026-07-12T08:43:43Z",
  },
};

const normalized = {
  schema_version: 1,
  dropTable: {
    rows: [
      {
        sources: [
          {
            title: "Beardling",
            url: "https://dontstarve.wiki.gg/wiki/Beardling",
            entityId: null,
          },
        ],
        quantity: "1-3",
        chance: "40%",
        context: null,
      },
    ],
  },
  usage: {
    recipes: [
      {
        result: {
          title: "Night Light",
          url: "https://dontstarve.wiki.gg/wiki/Night_Light",
          entityId: "base_game:nightlight",
        },
        resultAmount: 1,
        nightmareFuelAmount: 2,
        ingredients: [
          {
            item: {
              title: "Gold Nugget",
              url: "https://dontstarve.wiki.gg/wiki/Gold_Nugget",
              entityId: "base_game:goldnugget",
            },
            amount: 8,
          },
        ],
        station: "Prestihatitator",
        dlc: null,
        character: null,
        note: null,
      },
    ],
  },
};

describe("parseWikiPageDetail", () => {
  it("parses the exported schema and keeps only rendered fields", () => {
    expect(parseWikiPageDetail(validDetail)).toEqual({
      pageId: 100736,
      title: "Halberd",
      canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd",
      html: "<p>Pointy and hurty.</p>",
      categories: ["Items", "Weapons"],
      images: [
        {
          title: "File:Halberd.png",
          src: "/assets/wiki/halberd.png",
          mime: "image/png",
          width: 64,
          height: 64,
        },
      ],
      revision: {
        id: 569319,
        sha1: "5bf67f6c77b1a0d0c5bb66b0ef02ccf5c04dba64",
        timestamp: "2026-07-12T08:43:43Z",
      },
      normalized: null,
    });
  });

  it("parses normalized Drop table and Usage sections", () => {
    const parsed = parseWikiPageDetail({ ...validDetail, normalized });

    expect(parsed.normalized?.dropTable.rows).toHaveLength(1);
    expect(parsed.normalized?.usage.recipes[0]).toMatchObject({
      nightmareFuelAmount: 2,
      station: "Prestihatitator",
    });
  });

  it.each([
    { ...normalized, schema_version: 2 },
    { ...normalized, dropTable: { rows: [] } },
    { ...normalized, usage: { recipes: [] } },
    {
      ...normalized,
      dropTable: {
        rows: [{ ...normalized.dropTable.rows[0], sources: [] }],
      },
    },
    {
      ...normalized,
      usage: {
        recipes: [
          { ...normalized.usage.recipes[0], nightmareFuelAmount: 0 },
        ],
      },
    },
    {
      ...normalized,
      usage: {
        recipes: [{ ...normalized.usage.recipes[0], result: null }],
      },
    },
  ])("rejects malformed normalized sections", (value) => {
    expect(() =>
      parseWikiPageDetail({ ...validDetail, normalized: value }),
    ).toThrow();
  });

  it.each([
    { ...validDetail, schema_version: 2 },
    { ...validDetail, pageId: 0 },
    { ...validDetail, canonicalUrl: "" },
    { ...validDetail, categories: [1] },
    { ...validDetail, revision: null },
  ])("rejects an invalid detail contract", (value) => {
    expect(() => parseWikiPageDetail(value)).toThrow();
  });
});
