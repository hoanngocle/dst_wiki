import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { WikiEntry } from "@/app/lib/wiki-search";
import { WikiSearch } from "./wiki-search";

const entries: readonly WikiEntry[] = [
  {
    id: "ancient-blade",
    name: "Ancient Blade",
    category: "item",
    description: "A relic weapon from the northern ruins.",
    keywords: ["sword"],
    accent: "ice",
  },
  {
    id: "mire-stalker",
    name: "Mire Stalker",
    category: "creature",
    description: "A beast near flooded paths.",
    keywords: ["swamp"],
    accent: "moss",
  },
];

describe("WikiSearch", () => {
  it("shows every entry before the user filters", () => {
    render(<WikiSearch entries={entries} />);
    expect(screen.getByText("Ancient Blade")).toBeDefined();
    expect(screen.getByText("Mire Stalker")).toBeDefined();
    expect(screen.getByText("2 entries")).toBeDefined();
  });

  it("filters immediately as the user types", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Search the atlas" }), {
      target: { value: "mire" },
    });
    expect(screen.queryByText("Ancient Blade")).toBeNull();
    expect(screen.getByText("Mire Stalker")).toBeDefined();
    expect(screen.getByText("1 entry")).toBeDefined();
  });

  it("announces result context when equal-count result sets change", () => {
    render(<WikiSearch entries={entries} />);
    const search = screen.getByRole("searchbox", { name: "Search the atlas" });

    fireEvent.change(search, { target: { value: "ancient" } });
    const status = screen.getByRole("status");
    expect(status.textContent).toBe('1 entry matching "ancient" in All entries.');

    fireEvent.change(search, { target: { value: "mire" } });
    expect(status.textContent).toBe('1 entry matching "mire" in All entries.');
  });

  it("filters by category", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.click(screen.getByRole("button", { name: "Items" }));
    expect(screen.getByText("Ancient Blade")).toBeDefined();
    expect(screen.queryByText("Mire Stalker")).toBeNull();
  });

  it("keeps each result category visible and available to assistive technology on mobile", () => {
    render(<WikiSearch entries={entries} />);
    const ancientBladeRow = screen.getByText("Ancient Blade").closest("li");

    expect(ancientBladeRow).not.toBeNull();
    const category = within(ancientBladeRow as HTMLElement).getByText("item");
    expect(category.className.split(/\s+/)).toContain("inline-flex");
    expect(category.className.split(/\s+/)).not.toContain("hidden");
    expect(ancientBladeRow?.textContent).toContain("item");
  });

  it("exposes category filters as a named group", () => {
    render(<WikiSearch entries={entries} />);
    expect(screen.getByRole("group", { name: "Filter entries by category" })).toBeDefined();
  });

  it("clears query and category from the empty state", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.click(screen.getByRole("button", { name: "Items" }));
    fireEvent.change(screen.getByRole("searchbox", { name: "Search the atlas" }), {
      target: { value: "mire" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Clear filters" }));
    expect(screen.getByRole("searchbox", { name: "Search the atlas" })).toHaveProperty("value", "");
    expect(screen.getByRole("button", { name: "All entries" }).getAttribute("aria-pressed")).toBe("true");
  });

  it("highlights matching text", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Search the atlas" }), {
      target: { value: "blade" },
    });
    expect(screen.getByText("Blade").tagName).toBe("MARK");
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
    fireEvent.change(screen.getByRole("searchbox", { name: "Search the atlas" }), {
      target: { value: "cafe" },
    });

    expect(document.querySelector("mark")?.textContent).toBe("Cafe\u0301");
  });

  it("restarts result-boundary motion when filtering retains keyed rows", () => {
    render(<WikiSearch entries={entries} />);
    const firstBoundary = screen.getByRole("list");

    fireEvent.change(screen.getByRole("searchbox", { name: "Search the atlas" }), {
      target: { value: "ancient" },
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
    const search = screen.getByRole("searchbox", { name: "Search the atlas" });
    fireEvent.change(search, { target: { value: "mire" } });
    const clear = screen.getByRole("button", { name: "Clear search" });
    clear.focus();
    fireEvent.click(clear);
    expect(search).toHaveProperty("value", "");
    expect(document.activeElement).toBe(search);
  });

  it("keeps the clear search touch target at least 40px tall", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.change(screen.getByRole("searchbox", { name: "Search the atlas" }), {
      target: { value: "mire" },
    });

    const clear = screen.getByRole("button", { name: "Clear search" });
    expect(clear.className.split(/\s+/)).toContain("min-h-10");
  });

  it("focuses search when slash is pressed outside an editable control", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.keyDown(window, { key: "/" });
    expect(document.activeElement).toBe(screen.getByRole("searchbox", { name: "Search the atlas" }));
  });

  it("focuses search when Control K is pressed", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    expect(document.activeElement).toBe(screen.getByRole("searchbox", { name: "Search the atlas" }));
  });

  it("clears the query with Escape", () => {
    render(<WikiSearch entries={entries} />);
    const search = screen.getByRole("searchbox", { name: "Search the atlas" });
    fireEvent.change(search, { target: { value: "mire" } });
    fireEvent.keyDown(search, { key: "Escape" });
    expect(search).toHaveProperty("value", "");
  });
});
