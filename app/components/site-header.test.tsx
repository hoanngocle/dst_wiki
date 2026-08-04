import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import { SiteHeader } from "./site-header";

it("links the standalone navigation to Items, Nhân vật, and Hướng dẫn", () => {
  const { container } = render(<SiteHeader active="items" />);

  expect(screen.getByText("Don't Starve Together")).toBeDefined();
  expect(screen.getByRole("navigation", { name: /điều hướng chính/i })).toBeDefined();
  expect(screen.getByRole("link", { name: /vật phẩm/i }).getAttribute("href")).toBe("/");
  expect(screen.getByRole("link", { name: "Nhân vật" }).getAttribute("href")).toBe(
    "/characters",
  );
  expect(screen.getByRole("link", { name: /hướng dẫn/i }).getAttribute("href")).toBe(
    "/guides",
  );
  expect(screen.getByRole("link", { name: /vật phẩm/i }).getAttribute("aria-current")).toBe(
    "page",
  );
  expect(screen.queryByRole("link", { name: "Base" })).toBeNull();
  expect(container.innerHTML).not.toContain("/dst");
});

it("keeps vertical room for navigation link focus rings inside the scroll area", () => {
  render(<SiteHeader active="items" />);

  expect(screen.getByRole("navigation", { name: /điều hướng chính/i }).className).toContain(
    "py-1",
  );
});
