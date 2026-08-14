import { render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";

import { SiteHeader } from "./site-header";

it("links the standalone navigation to Vật phẩm, Chế tạo Tu Tiên, and Cảnh giới Tu Tiên", () => {
  const { container } = render(<SiteHeader active="items" />);

  expect(screen.getByText("Don't Starve Together")).toBeDefined();
  const navigation = screen.getByRole("navigation", { name: /điều hướng chính/i });
  expect(within(navigation).getAllByRole("link").map((link) => link.textContent)).toEqual([
    "Vật phẩm",
    "Chế tạo Tu Tiên",
    "Cảnh giới Tu Tiên",
  ]);
  expect(screen.getByRole("link", { name: /vật phẩm/i }).getAttribute("href")).toBe("/");
  expect(screen.getByRole("link", { name: "Chế tạo Tu Tiên" }).getAttribute("href")).toBe(
    "/tu-tien-crafting",
  );
  expect(screen.getByRole("link", { name: "Cảnh giới Tu Tiên" }).getAttribute("href")).toBe("/tu-tien");
  expect(screen.getByRole("link", { name: /vật phẩm/i }).getAttribute("aria-current")).toBe(
    "page",
  );
  expect(screen.queryByRole("link", { name: "Nhân vật" })).toBeNull();
  expect(screen.queryByRole("link", { name: "Base" })).toBeNull();
  expect(screen.queryByRole("link", { name: /hướng dẫn/i })).toBeNull();
  expect(container.innerHTML).not.toContain("/dst");
});

it("marks the crafting tab as active on the Hàn Lập crafting page", () => {
  render(<SiteHeader active="tu-tien-crafting" />);

  expect(screen.getByRole("link", { name: "Chế tạo Tu Tiên" }).getAttribute("aria-current")).toBe(
    "page",
  );
});

it("marks the cultivation tab as active on the Tu Tiên page", () => {
  render(<SiteHeader active="tu-tien" />);

  expect(screen.getByRole("link", { name: "Cảnh giới Tu Tiên" }).getAttribute("aria-current")).toBe(
    "page",
  );
});

it("keeps vertical room for navigation link focus rings inside the scroll area", () => {
  render(<SiteHeader active="items" />);

  expect(screen.getByRole("navigation", { name: /điều hướng chính/i }).className).toContain(
    "py-1",
  );
});
