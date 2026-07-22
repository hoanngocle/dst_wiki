import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import type { GuideDetail } from "@/app/lib/guide-catalog";
import { GuideReader } from "./guide-reader";

const guide: GuideDetail = {
  schemaVersion: 1,
  id: "guide:beefalo",
  slug: "beefalo",
  title: "Taming a Beefalo",
  titleVi: "Thuần hóa Beefalo",
  summaryVi: "Hướng dẫn thuần hóa.",
  sourceUrl: "https://dontstarve.fandom.com/wiki/Guides/Taming_a_Beefalo",
  cover: { src: "/assets/guides/beefalo.jpg", alt: "Beefalo", width: 1152, height: 571, sha256: "abc" },
  topic: "domestication",
  audience: "intermediate",
  readingMinutes: 4,
  revision: { id: 7, timestamp: "2026-07-22T00:00:00Z", sha1: "sha" },
  toc: [{ id: "bat-dau", label: "Bắt đầu", level: 2 }],
  sections: [
    { id: "overview", heading: "Tổng quan", level: 1, html: "<p>Giới thiệu</p>" },
    { id: "bat-dau", heading: "Bắt đầu", level: 2, html: '<h2 id="bat-dau">Bắt đầu</h2><p>Nội dung</p>' },
  ],
};

it("renders a dedicated article with cover, toc, sections, and source attribution", () => {
  render(<GuideReader guide={guide} />);
  expect(screen.getByRole("heading", { name: "Thuần hóa Beefalo", level: 1 })).toBeDefined();
  expect(screen.getByRole("navigation", { name: "Mục lục hướng dẫn" })).toBeDefined();
  expect(screen.getByRole("link", { name: "Bắt đầu" }).getAttribute("href")).toBe("#bat-dau");
  expect(screen.getByText("Nội dung")).toBeDefined();
  expect(
    screen.getAllByRole("link", { name: /Xem nguồn Fandom/ }).every(
      (link) => link.getAttribute("href") === guide.sourceUrl,
    ),
  ).toBe(true);
});
