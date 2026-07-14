import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import Home from "./page";
import { wikiEntries } from "./data/wiki-entries";

it("renders the Frost Atlas search shell", () => {
  render(<Home />);
  expect(screen.getByText("FROST ATLAS")).toBeDefined();
  expect(screen.getByRole("heading", { level: 1, name: /Find answers/i })).toBeDefined();
  expect(screen.getByRole("searchbox", { name: "Search the atlas" })).toBeDefined();
});

it("hides the header entry count below the 768px breakpoint", () => {
  render(<Home />);
  const entryCount = screen
    .getAllByText(`${wikiEntries.length} entries`)
    .find((element) => element.closest("header"));

  expect(entryCount).toBeDefined();
  expect(entryCount?.className.split(/\s+/)).toContain("md:block");
  expect(entryCount?.className.split(/\s+/)).not.toContain("sm:block");
});
