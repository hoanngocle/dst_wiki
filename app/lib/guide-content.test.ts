import { describe, expect, it } from "vitest";

import { parseGuideDetail, parseGuideIndex, type GuideDetail, type GuideIndex } from "./guide-catalog";
import * as guideContent from "./guide-content";
import giants from "@/public/data/guides/pages/how-to-kill-the-giants-in-dst.json";
import base from "@/public/data/guides/pages/maximum-efficiency-day-13-base-dst-guide.json";
import slime from "@/public/data/guides/pages/slurtle-slime-guide.json";
import beefalo from "@/public/data/guides/pages/taming-a-beefalo.json";

import { findGuide, guideSlugs } from "./guide-content";

const guides = [giants, base, slime, beefalo];

describe("published Guide translations", () => {
  it("contains Vietnamese prose and no crawler heading noise", () => {
    const articleText = guides
      .flatMap((guide) => guide.sections)
      .map((section) => `${section.heading} ${section.html}`)
      .join(" ");
    const tocLabels = guides.flatMap((guide) => guide.toc.map((row) => row.label));

    expect(articleText).toContain("Thuần hóa Beefalo");
    expect(articleText).toContain("Slurtle Slime được tạo ra");
    expect(articleText).not.toMatch(/\b(?:This guide|Taming a Beefalo|Process of Taming|Statistics and Tendencies)\b/);
    expect(tocLabels).not.toContain("Contents");
    expect(tocLabels.every((label) => !label.endsWith("[]"))).toBe(true);
  });

  it("publishes exactly the reviewed article registry in index order", () => {
    expect(guideSlugs()).toEqual([
      "how-to-kill-the-giants-in-dst",
      "maximum-efficiency-day-13-base-dst-guide",
      "slurtle-slime-guide",
      "taming-a-beefalo",
    ]);
    expect(findGuide("taming-a-beefalo")?.titleVi).toBe("Thuần hóa Beefalo");
    expect(findGuide("canh-gioi-tu-tien")).toBeUndefined();
    expect(findGuide("unpublished-guide")).toBeUndefined();
  });

  it("rejects a detail whose cover metadata differs from its reviewed index entry", () => {
    const buildGuideRegistry = (
      guideContent as typeof guideContent & {
        buildGuideRegistry: (index: GuideIndex, details: readonly GuideDetail[]) => unknown;
      }
    ).buildGuideRegistry;
    const index = parseGuideIndex({
      schemaVersion: 1,
      count: 1,
      guides: [{ ...beefalo }],
    });
    const detail = parseGuideDetail({
      ...beefalo,
      cover: { ...beefalo.cover, alt: "Ảnh bìa đã bị thay đổi" },
    });

    expect(() => buildGuideRegistry(index, [detail])).toThrow(
      /published Guide detail does not match its index entry/,
    );
  });
});
