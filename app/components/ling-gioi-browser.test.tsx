import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it } from "vitest";
import { LingGioiBrowser } from "./ling-gioi-browser";

const sections = [{ id: "jingjie", name: "Cảnh giới" }, { id: "log", name: "Nhật ký cập nhật" }];
const items = [{ id: "realm_system", section: "jingjie", name: "Hệ thống cảnh giới", summary: "Chín cảnh giới.", recipe: "", details: "Mỗi cảnh giới có 9 bậc.\n\n[[图片:images/badge.png|Huy hiệu cảnh giới]]", tags: ["Tu luyện"], image: "", originalName: "境界体系", order: 1 }];

afterEach(() => { window.history.replaceState(null, "", "/"); });

it("searches Vietnamese without accents and opens the full article", async () => {
  render(<LingGioiBrowser sections={sections} items={items} />);
  fireEvent.change(screen.getByRole("searchbox"), { target: { value: "canh gioi" } });
  const card = screen.getByRole("button", { name: /Hệ thống cảnh giới/ });
  fireEvent.click(card);
  expect(screen.getByRole("dialog").textContent).toContain("Mỗi cảnh giới có 9 bậc.");
  expect(screen.getByAltText("Huy hiệu cảnh giới").getAttribute("src")).toBe("/ling-gioi/images/badge.png");
  fireEvent.click(screen.getByRole("button", { name: "Đóng" }));
  expect(screen.queryByRole("dialog")).toBeNull();
  await waitFor(() => expect(document.activeElement).toBe(card));
});

it("shows an honest empty state for source sections without entries", () => {
  render(<LingGioiBrowser sections={sections} items={items} />);
  fireEvent.click(screen.getByRole("button", { name: /Nhật ký cập nhật/ }));
  expect(screen.getByText("Trang nguồn chưa có nội dung trong mục này.")).toBeDefined();
});

it("opens shared source-style deep links directly", () => {
  window.history.replaceState(null, "", "/linh-gioi#sec=jingjie&item=realm_system");
  render(<LingGioiBrowser sections={sections} items={items} />);
  expect(screen.getByRole("dialog").textContent).toContain("Hệ thống cảnh giới");
  fireEvent.click(screen.getByRole("button", { name: "Đóng" }));
  expect(screen.getByRole("button", { name: /^Cảnh giới/ }).getAttribute("aria-pressed")).toBe("true");
});

it("links named items in article text to their own details", () => {
  window.history.replaceState(null, "", "/linh-gioi#item=realm_system");
  render(<LingGioiBrowser sections={sections} items={[{ ...items[0], details: "Dùng Linh Thạch để luyện chế." }, { ...items[0], id: "stone", name: "Linh Thạch", details: "Vật liệu luyện chế." }]} />);
  screen.getByRole("dialog").scrollTop = 300;
  fireEvent.click(screen.getByRole("button", { name: "Linh Thạch" }));
  expect(screen.getByRole("dialog").textContent).toContain("Vật liệu luyện chế.");
  expect(screen.getByRole("dialog").scrollTop).toBe(0);
  expect(document.activeElement).toBe(screen.getByRole("heading", { name: "Linh Thạch" }));
});
