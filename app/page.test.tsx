import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import Home from "./page";

it("renders the Frost Atlas search shell", () => {
  render(<Home />);
  expect(screen.getByText("FROST ATLAS")).toBeDefined();
  expect(screen.getByRole("heading", { level: 1, name: /Find answers/i })).toBeDefined();
  expect(screen.getByRole("searchbox", { name: "Search the atlas" })).toBeDefined();
});
