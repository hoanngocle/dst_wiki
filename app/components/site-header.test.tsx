import { render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";

import { SiteHeader } from "./site-header";

it("links the standalone navigation in the approved order", () => {
  const { container } = render(<SiteHeader active="items" />);

  expect(screen.getByText("Don't Starve Together")).toBeDefined();
  const navigation = screen.getByRole("navigation", { name: /điều hướng chính/i });
  expect(within(navigation).getAllByRole("link").map((link) => link.textContent)).toEqual([
    "Vật phẩm",
    "Phàm Nhân",
    "Chế tạo Tu Tiên",
    "Cảnh giới Tu Tiên",
    "Solo Leveling",
    "Linh Giới",
  ]);
  expect(screen.getByRole("link", { name: /vật phẩm/i }).getAttribute("href")).toBe("/");
  expect(screen.getByRole("link", { name: "Chế tạo Tu Tiên" }).getAttribute("href")).toBe(
    "/tu-tien-crafting",
  );
  expect(screen.getByRole("link", { name: "Cảnh giới Tu Tiên" }).getAttribute("href")).toBe(
    "/tu-tien",
  );
  expect(screen.getByRole("link", { name: /vật phẩm/i }).getAttribute("aria-current")).toBe(
    "page",
  );
  expect(screen.queryByRole("link", { name: "Nhân vật" })).toBeNull();
  expect(screen.queryByRole("link", { name: "Base" })).toBeNull();
  expect(screen.queryByRole("link", { name: /hướng dẫn/i })).toBeNull();
  expect(container.innerHTML).not.toContain("/dst");
});

it("links and marks the Phàm Nhân tab active", () => {
  render(<SiteHeader active="tu-tien-ky" />);
  const link = screen.getByRole("link", { name: "Phàm Nhân" });
  expect(link.getAttribute("href")).toBe("/pham-nhan-tu-tien");
  expect(link.getAttribute("aria-current")).toBe("page");
});

it("links and marks the Solo Leveling tab active", () => {
  render(<SiteHeader active="solo-leveling" />);
  const link = screen.getByRole("link", { name: "Solo Leveling" });
  expect(link.getAttribute("href")).toBe("/solo-leveling");
  expect(link.getAttribute("aria-current")).toBe("page");
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
