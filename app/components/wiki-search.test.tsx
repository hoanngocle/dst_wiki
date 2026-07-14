import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { wikiEntries } from "@/app/data/wiki-entries";
import type { WikiEntry } from "@/app/lib/wiki-search";
import { WikiSearch } from "./wiki-search";

const searchName = "Tìm kiếm Items.";

const entries: readonly WikiEntry[] = [
  {
    id: "ancient-blade",
    name: "Lưỡi Kiếm Cổ",
    category: "item",
    description: "Một vũ khí cổ từ tàn tích phương bắc.",
    keywords: ["kiếm", "vũ khí", "vật phẩm"],
    accent: "ice",
  },
  {
    id: "mire-stalker",
    name: "Kẻ Rình Đầm Lầy",
    category: "creature",
    description: "Một sinh vật bên những lối đi ngập nước.",
    keywords: ["đầm lầy", "sinh vật"],
    accent: "moss",
  },
];

describe("WikiSearch", () => {
  it("shows every entry before the user filters", () => {
    render(<WikiSearch entries={entries} />);
    expect(screen.getByText("Lưỡi Kiếm Cổ")).toBeDefined();
    expect(screen.getByText("Kẻ Rình Đầm Lầy")).toBeDefined();
    expect(screen.getByText("2 mục")).toBeDefined();
  });

  it("filters immediately as the user types", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.change(screen.getByRole("searchbox", { name: searchName }), {
      target: { value: "đầm lầy" },
    });
    expect(screen.queryByText("Lưỡi Kiếm Cổ")).toBeNull();
    expect(screen.getByText("Kẻ Rình Đầm Lầy")).toBeDefined();
    expect(screen.getByText("1 mục")).toBeDefined();
  });

  it("announces result context when equal-count result sets change", () => {
    render(<WikiSearch entries={entries} />);
    const search = screen.getByRole("searchbox", { name: searchName });

    fireEvent.change(search, { target: { value: "cổ" } });
    const status = screen.getByRole("status");
    expect(status.textContent).toBe('1 mục khớp với "cổ" trong Tất cả.');

    fireEvent.change(search, { target: { value: "đầm lầy" } });
    expect(status.textContent).toBe('1 mục khớp với "đầm lầy" trong Tất cả.');
  });

  it("filters by category", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.click(screen.getByRole("button", { name: "Vật phẩm" }));
    expect(screen.getByText("Lưỡi Kiếm Cổ")).toBeDefined();
    expect(screen.queryByText("Kẻ Rình Đầm Lầy")).toBeNull();
  });

  it("keeps each result category visible and available to assistive technology on mobile", () => {
    render(<WikiSearch entries={entries} />);
    const ancientBladeRow = screen.getByText("Lưỡi Kiếm Cổ").closest("li");

    expect(ancientBladeRow).not.toBeNull();
    const category = within(ancientBladeRow as HTMLElement).getByText("Vật phẩm");
    expect(category.className.split(/\s+/)).toContain("inline-flex");
    expect(category.className.split(/\s+/)).not.toContain("hidden");
    expect(ancientBladeRow?.textContent).toContain("Vật phẩm");
  });

  it("exposes category filters as a named group", () => {
    render(<WikiSearch entries={entries} />);
    expect(screen.getByRole("group", { name: "Lọc mục theo danh mục" })).toBeDefined();
  });

  it("clears query and category from the empty state", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.click(screen.getByRole("button", { name: "Vật phẩm" }));
    fireEvent.change(screen.getByRole("searchbox", { name: searchName }), {
      target: { value: "đầm lầy" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Xoá bộ lọc" }));
    expect(screen.getByRole("searchbox", { name: searchName })).toHaveProperty("value", "");
    expect(screen.getByRole("button", { name: "Tất cả" }).getAttribute("aria-pressed")).toBe(
      "true",
    );
  });

  it("highlights matching text", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.change(screen.getByRole("searchbox", { name: searchName }), {
      target: { value: "kiếm" },
    });
    expect(screen.getByText("Kiếm").tagName).toBe("MARK");
  });

  it("highlights the complete original grapheme for decomposed Unicode text", () => {
    const decomposedEntries: readonly WikiEntry[] = [
      {
        id: "cafe-trail",
        name: "Cafe\u0301 Trail",
        category: "location",
        description: "A quiet route beside the ridge.",
        keywords: ["cafe"],
        accent: "slate",
      },
    ];

    render(<WikiSearch entries={decomposedEntries} />);
    fireEvent.change(screen.getByRole("searchbox", { name: searchName }), {
      target: { value: "cafe" },
    });

    expect(document.querySelector("mark")?.textContent).toBe("Cafe\u0301");
  });

  it("restarts result-boundary motion when filtering retains keyed rows", () => {
    render(<WikiSearch entries={entries} />);
    const firstBoundary = screen.getByRole("list");

    fireEvent.change(screen.getByRole("searchbox", { name: searchName }), {
      target: { value: "cổ" },
    });

    const nextBoundary = screen.getByRole("list");
    expect(nextBoundary).not.toBe(firstBoundary);
    expect(nextBoundary.className).toContain(
      "motion-safe:animate-[atlas-result-in_180ms_ease-out]",
    );
    expect(within(nextBoundary).getByRole("listitem").className).not.toContain(
      "motion-safe:animate-[atlas-result-in_180ms_ease-out]",
    );
  });

  it("returns focus to search after clearing the query", () => {
    render(<WikiSearch entries={entries} />);
    const search = screen.getByRole("searchbox", { name: searchName });
    fireEvent.change(search, { target: { value: "đầm lầy" } });
    const clear = screen.getByRole("button", { name: "Xoá tìm kiếm" });
    clear.focus();
    fireEvent.click(clear);
    expect(search).toHaveProperty("value", "");
    expect(document.activeElement).toBe(search);
  });

  it("keeps the clear search touch target at least 44px tall", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.change(screen.getByRole("searchbox", { name: searchName }), {
      target: { value: "đầm lầy" },
    });

    const clear = screen.getByRole("button", { name: "Xoá tìm kiếm" });
    expect(clear.className.split(/\s+/)).toContain("min-h-11");
  });

  it("focuses search when slash is pressed outside an editable control", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.keyDown(window, { key: "/" });
    expect(document.activeElement).toBe(screen.getByRole("searchbox", { name: searchName }));
  });

  it("focuses search when Control K is pressed", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    expect(document.activeElement).toBe(screen.getByRole("searchbox", { name: searchName }));
  });

  it("clears the query with Escape", () => {
    render(<WikiSearch entries={entries} />);
    const search = screen.getByRole("searchbox", { name: searchName });
    fireEvent.change(search, { target: { value: "đầm lầy" } });
    fireEvent.keyDown(search, { key: "Escape" });
    expect(search).toHaveProperty("value", "");
  });

  it("finds Vietnamese text when the query omits diacritics", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.change(screen.getByRole("searchbox", { name: searchName }), {
      target: { value: "vu khi" },
    });
    expect(screen.getByText("Lưỡi Kiếm Cổ")).toBeDefined();
  });

  it.each([
    ["vật phẩm", "Lưỡi Kiếm Cổ"],
    ["sinh vật", "Kẻ Rình Đầm Lầy"],
    ["địa điểm", "Đài Quan Sát Windrest"],
    ["nhiệm vụ", "Tấm Bản Đồ Mượn"],
  ])("finds the Vietnamese %s category", (query, expectedName) => {
    render(<WikiSearch entries={wikiEntries} />);
    fireEvent.change(screen.getByRole("searchbox", { name: searchName }), {
      target: { value: query },
    });
    expect(screen.getByText(expectedName)).toBeDefined();
  });
});
