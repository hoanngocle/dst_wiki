import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import type { GuideListEntry } from "@/app/lib/guide-catalog";
import { GuideBrowser } from "./guide-browser";

const guides: GuideListEntry[] = [
  {
    id: "guide:beefalo",
    slug: "beefalo",
    title: "Taming a Beefalo",
    titleVi: "Thuần hóa Beefalo",
    summaryVi: "Tăng obedience và domestication.",
    sourceUrl: "https://dontstarve.fandom.com/wiki/Guides/Taming_a_Beefalo",
    cover: { src: "/assets/guides/beefalo.jpg", alt: "Beefalo", width: 1152, height: 571, sha256: "a" },
    topic: "domestication",
    audience: "intermediate",
    readingMinutes: 4,
  },
  {
    id: "guide:giants",
    slug: "giants",
    title: "How to Kill Giants",
    titleVi: "Đánh bại Giant",
    summaryVi: "Chuẩn bị cho những trận đánh lớn.",
    sourceUrl: "https://dontstarve.fandom.com/wiki/Guides/Giants",
    cover: { src: "/assets/guides/giants.jpg", alt: "Giant", width: 1920, height: 1080, sha256: "b" },
    topic: "combat",
    audience: "advanced",
    readingMinutes: 6,
  },
];

it("searches, filters, resets, and links to dedicated Guide pages", () => {
  render(<GuideBrowser guides={guides} />);
  expect(screen.getByText("2 hướng dẫn")).toBeDefined();
  expect(screen.getByRole("link", { name: /Thuần hóa Beefalo/ }).getAttribute("href")).toBe(
    "/guides/beefalo",
  );
  expect(screen.getAllByRole("img")[0].getAttribute("width")).toBeTruthy();

  fireEvent.change(screen.getByLabelText("Tìm hướng dẫn"), { target: { value: "thuan hoa" } });
  expect(screen.getByText("1 hướng dẫn")).toBeDefined();
  expect(screen.queryByText("Đánh bại Giant")).toBeNull();

  fireEvent.click(screen.getByRole("button", { name: "Đặt lại bộ lọc" }));
  fireEvent.change(screen.getByLabelText("Chủ đề"), { target: { value: "combat" } });
  expect(screen.getByText("Đánh bại Giant")).toBeDefined();
  expect(screen.queryByText("Thuần hóa Beefalo")).toBeNull();

  fireEvent.change(screen.getByLabelText("Trình độ"), { target: { value: "intermediate" } });
  expect(screen.getByText("Không tìm thấy hướng dẫn phù hợp")).toBeDefined();
});
