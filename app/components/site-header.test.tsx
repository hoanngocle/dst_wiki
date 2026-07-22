import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import { SiteHeader } from "./site-header";

it("links the shared navigation to Prefabs, Nhân vật, Base, and Guide", () => {
  render(<SiteHeader active="items" />);
  expect(screen.getByText("Don't Starve Together")).toBeDefined();
  expect(screen.getByRole("link", { name: "Prefabs" }).getAttribute("href")).toBe("/");
  expect(screen.getByRole("link", { name: "Base" }).getAttribute("href")).toBe("/base");
  expect(screen.getByRole("link", { name: "Nhân vật" }).getAttribute("href")).toBe(
    "/characters",
  );
  expect(screen.getByRole("link", { name: "Guide" }).getAttribute("href")).toBe(
    "/guides",
  );
  expect(screen.getByRole("link", { name: "Prefabs" }).getAttribute("aria-current")).toBe(
    "page",
  );
});
