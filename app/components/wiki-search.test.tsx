import { fireEvent, render, screen } from "@testing-library/react";
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

  it("filters by category", () => {
    render(<WikiSearch entries={entries} />);
    fireEvent.click(screen.getByRole("button", { name: "Items" }));
    expect(screen.getByText("Ancient Blade")).toBeDefined();
    expect(screen.queryByText("Mire Stalker")).toBeNull();
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
