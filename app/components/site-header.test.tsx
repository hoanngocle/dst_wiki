import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import { SiteHeader } from "./site-header";

it("links the shared navigation to Items and Base", () => {
  render(<SiteHeader active="items" />);
  expect(screen.getByText("Don't Starve Together")).toBeDefined();
  expect(screen.getByRole("link", { name: "Items" }).getAttribute("href")).toBe("/");
  expect(screen.getByRole("link", { name: "Base" }).getAttribute("href")).toBe("/base");
  expect(screen.getByRole("link", { name: "Items" }).getAttribute("aria-current")).toBe(
    "page",
  );
});
