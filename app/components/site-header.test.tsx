import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";

import { SiteHeader } from "./site-header";

it("links the standalone navigation in the approved order", () => {
  const { container } = render(<SiteHeader active="items" />);

  expect(screen.getByText("Don't Starve Together")).toBeDefined();
  const navigation = screen.getByRole("navigation", { name: /điều hướng chính/i });
  expect(within(navigation).getAllByRole("link").map((link) => link.textContent)).toEqual([
    "Vật phẩm",
    "Tu Tiên",
    "Solo Leveling",
    "Linh Giới",
    "Lộ trình boss",
  ]);
  expect(screen.getByRole("link", { name: /vật phẩm/i }).getAttribute("href")).toBe("/");
  expect(screen.getByRole("link", { name: "Tu Tiên" }).getAttribute("href")).toBe("/tu-tien");
  expect(screen.queryByRole("link", { name: "Achievement & Level" })).toBeNull();
  expect(screen.getByRole("link", { name: /vật phẩm/i }).getAttribute("aria-current")).toBe(
    "page",
  );
  expect(screen.queryByRole("link", { name: "Nhân vật" })).toBeNull();
  expect(screen.queryByRole("link", { name: "Base" })).toBeNull();
  expect(screen.queryByRole("link", { name: /hướng dẫn/i })).toBeNull();
  expect(container.innerHTML).not.toContain("/dst");
});

it("does not publish a NOVA navigation tab", () => {
  render(<SiteHeader active="items" />);
  expect(screen.queryByRole("link", { name: "NOVA" })).toBeNull();
});

it("links and marks the Solo Leveling tab active", () => {
  render(<SiteHeader active="solo-leveling" />);
  const link = screen.getByRole("link", { name: "Solo Leveling" });
  expect(link.getAttribute("href")).toBe("/solo-leveling");
  expect(link.getAttribute("aria-current")).toBe("page");
});

it("opens the Tu Tien submenu by hover and button, with direct mod links", () => {
  render(<SiteHeader active="tu-tien" />);
  const mainLink = screen.getByRole("link", { name: "Tu Tiên" });
  expect(mainLink.getAttribute("aria-current")).toBe("page");
  fireEvent(mainLink.parentElement!, Object.assign(new Event("pointerover", { bubbles: true }), { pointerType: "mouse" }));
  expect(screen.getByRole("link", { name: "Thần Khí" }).getAttribute("href")).toBe("/tu-tien#than-khi");
  fireEvent(mainLink.parentElement!, Object.assign(new Event("pointerout", { bubbles: true }), { pointerType: "mouse" }));
  expect(screen.queryByRole("link", { name: "Thần Khí" })).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Mở các mục Tu Tiên" }));
  expect(screen.queryByRole("link", { name: "Tiện Ích Client" })).toBeNull();
  expect(screen.queryByRole("link", { name: "Tiện Ích Tu Tiên" })).toBeNull();
  expect(screen.queryByRole("link", { name: "Trang Phục" })).toBeNull();
  expect(screen.getByRole("link", { name: "Nyx" })).toBeDefined();
  fireEvent.keyDown(screen.getByRole("button", { name: "Đóng các mục Tu Tiên" }), { key: "Escape" });
  expect(screen.queryByRole("link", { name: "Thần Khí" })).toBeNull();
});
it("keeps vertical room for navigation link focus rings inside the scroll area", () => {
  render(<SiteHeader active="items" />);

  expect(screen.getByRole("navigation", { name: /điều hướng chính/i }).className).toContain(
    "py-1",
  );
});

it("opens with a single touch without triggering mouse hover", () => {
  render(<SiteHeader active="tu-tien" />);
  const button = screen.getByRole("button", { name: "Mở các mục Tu Tiên" });
  fireEvent(button, Object.assign(new Event("pointerover", { bubbles: true }), { pointerType: "touch" }));
  expect(button.getAttribute("aria-expanded")).toBe("false");
  fireEvent.click(button);
  expect(button.getAttribute("aria-expanded")).toBe("true");
});
