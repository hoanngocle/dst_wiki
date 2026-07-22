import { describe, expect, it } from "vitest";

import { filterGuides, parseGuideDetail, parseGuideIndex } from "./guide-catalog";

const entry = {
  id: "guide:thuan-hoa-beefalo",
  slug: "thuan-hoa-beefalo",
  title: "Taming a Beefalo",
  titleVi: "Thuần hóa Beefalo",
  summaryVi: "Hướng dẫn obedience và domestication.",
  sourceUrl: "https://dontstarve.fandom.com/wiki/Guides/Taming_a_Beefalo",
  cover: {
    src: "/assets/guides/beefalo.jpg",
    alt: "Thuần hóa Beefalo",
    width: 1152,
    height: 571,
    sha256: "abc",
  },
  topic: "domestication",
  audience: "intermediate",
  readingMinutes: 4,
};

describe("guide catalog contract", () => {
  it("parses a strict index and detail payload", () => {
    const index = parseGuideIndex({ schemaVersion: 1, count: 1, guides: [entry] });
    const detail = parseGuideDetail({
      ...entry,
      schemaVersion: 1,
      revision: { id: 7, timestamp: "2026-07-22T00:00:00Z", sha1: "sha" },
      toc: [{ id: "bat-dau", label: "Bắt đầu", level: 2 }],
      sections: [{ id: "bat-dau", heading: "Bắt đầu", level: 2, html: "<p>Nội dung</p>" }],
    });

    expect(index.guides[0].slug).toBe("thuan-hoa-beefalo");
    expect(detail.sections[0].id).toBe("bat-dau");
  });

  it("rejects duplicate IDs, slugs, anchors, and missing content", () => {
    expect(() =>
      parseGuideIndex({ schemaVersion: 1, count: 2, guides: [entry, entry] }),
    ).toThrow(/duplicate guide id/);
    expect(() =>
      parseGuideIndex({
        schemaVersion: 1,
        count: 2,
        guides: [entry, { ...entry, id: "guide:other" }],
      }),
    ).toThrow(/duplicate guide slug/);
    expect(() =>
      parseGuideDetail({
        ...entry,
        schemaVersion: 1,
        revision: { id: 7, timestamp: "2026-07-22", sha1: "sha" },
        toc: [
          { id: "same", label: "Một", level: 2 },
          { id: "same", label: "Hai", level: 2 },
        ],
        sections: [{ id: "same", heading: "Một", level: 2, html: "<p>x</p>" }],
      }),
    ).toThrow(/duplicate guide anchor/);
    expect(() =>
      parseGuideIndex({ schemaVersion: 1, count: 1, guides: [{ ...entry, summaryVi: "" }] }),
    ).toThrow(/summaryVi/);
  });

  it("filters accent-insensitively by query, topic, and audience", () => {
    const guides = parseGuideIndex({
      schemaVersion: 1,
      count: 2,
      guides: [
        entry,
        {
          ...entry,
          id: "guide:giants",
          slug: "giants",
          title: "How to Kill Giants",
          titleVi: "Đánh bại Giant",
          topic: "combat",
          audience: "advanced",
        },
      ],
    }).guides;

    expect(filterGuides(guides, "thuan hoa", "all", "all")).toHaveLength(1);
    expect(filterGuides(guides, "", "combat", "all")[0].slug).toBe("giants");
    expect(filterGuides(guides, "", "all", "advanced")[0].slug).toBe("giants");
  });
});
