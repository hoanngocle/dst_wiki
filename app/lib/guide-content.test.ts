import { describe, expect, it } from "vitest";

import giants from "@/public/data/guides/pages/how-to-kill-the-giants-in-dst.json";
import base from "@/public/data/guides/pages/maximum-efficiency-day-13-base-dst-guide.json";
import slime from "@/public/data/guides/pages/slurtle-slime-guide.json";
import beefalo from "@/public/data/guides/pages/taming-a-beefalo.json";

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
});
