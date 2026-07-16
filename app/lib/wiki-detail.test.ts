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
    });
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
