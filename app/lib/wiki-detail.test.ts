import { describe, expect, it } from "vitest";

import * as wikiDetail from "./wiki-detail";
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
  schema_version: 2,
  subject: {
    title: "Nightmare Fuel",
    url: "https://dontstarve.wiki.gg/wiki/Nightmare_Fuel",
    entityId: "base_game:nightmarefuel",
  },
  dropTable: {
    rows: [
      {
        sources: [
          {
            title: "Beardling",
            url: "https://dontstarve.wiki.gg/wiki/Beardling",
            entityId: null,
            iconUrl:
              "https://dontstarve.wiki.gg/wiki/Special:Redirect/file/Beardling.png",
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
        subjectAmount: 2,
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
  it("builds the public static Wiki detail URL from a page identity", () => {
    const buildWikiDetailUrl = (
      wikiDetail as typeof wikiDetail & {
        buildWikiDetailUrl: (page: { pageId: number }) => string;
      }
    ).buildWikiDetailUrl;

    expect(buildWikiDetailUrl({ pageId: 105588 })).toBe(
      "/data/wiki/pages/105588.json",
    );
  });

  it("parses the exported schema and keeps only rendered fields", () => {
    expect(parseWikiPageDetail(validDetail)).toEqual({
      pageId: 100736,
      title: "Halberd",
      canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd",
      html: "<p>Pointy and hurty.</p>",
      summaryViHtml: null,
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

  it("parses an optional Vietnamese summary", () => {
    const summaryViHtml = "<h2>Tóm tắt</h2><p>Vũ khí cận chiến.</p>";

    expect(
      parseWikiPageDetail({ ...validDetail, summaryViHtml }).summaryViHtml,
    ).toBe(summaryViHtml);
  });

  it("accepts the tags, attributes, and HTTP URLs emitted by the Wiki sanitizer", () => {
    const html = [
      '<section id="overview" class="wiki-section">',
      '<h2 title="Overview">Overview</h2>',
      '<a href="https://dontstarve.wiki.gg/wiki/Halberd">',
      '<img src="https://dontstarve.wiki.gg/images/halberd.png" alt="Halberd" width="64" height="64">',
      "</a><br><table><tbody><tr><th colspan=\"2\">Stats</th></tr></tbody></table>",
      "</section>",
    ].join("");

    expect(parseWikiPageDetail({ ...validDetail, html }).html).toBe(html);
  });

  it("parses normalized Drop table and Usage sections", () => {
    const parsed = parseWikiPageDetail({ ...validDetail, normalized });

    expect(parsed.normalized?.dropTable.rows).toHaveLength(1);
    expect(parsed.normalized?.dropTable.rows[0].sources[0].iconUrl).toBe(
      "https://dontstarve.wiki.gg/wiki/Special:Redirect/file/Beardling.png",
    );
    expect(parsed.normalized?.usage.recipes[0]).toMatchObject({
      subjectAmount: 2,
      station: "Prestihatitator",
    });
  });

  it.each([
    { ...normalized, schema_version: 1 },
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
          { ...normalized.usage.recipes[0], subjectAmount: 0 },
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
    { ...validDetail, html: "<script>alert(1)</script>" },
    {
      ...validDetail,
      summaryViHtml: '<a href="javascript:alert(1)">Unsafe</a>',
    },
    {
      ...validDetail,
      html: '<a href="java&#x73;cript:alert(1)">Unsafe</a>',
    },
    { ...validDetail, html: "<img/onerror=alert(1)>" },
  ])("rejects an invalid detail contract", (value) => {
    expect(() => parseWikiPageDetail(value)).toThrow();
  });
});
