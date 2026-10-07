import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import Page from "./page";

it("shows furnace recipes and lets readers inspect a previously missing recipe and its ingredients", () => {
  render(<Page />);
  expect(screen.getByRole("heading", { level: 1, name: "Chế tạo Tu Tiên" })).toBeDefined();
  expect(screen.getByRole("button", { name: "Đan Lô (78)" }).getAttribute("aria-pressed")).toBe("true");
  expect(screen.getByText("Vũ khí chuyên thuộc")).toBeDefined();
  fireEvent.change(screen.getByRole("searchbox"), { target: { value: "Thiên Nghịch Châu" } });
  fireEvent.click(screen.getByRole("button", { name: "Xem chi tiết Thiên Nghịch Châu" }));
  const modal = screen.getByRole("dialog", { name: "Thiên Nghịch Châu" });
  expect(within(modal).getByText(/Luyện tại Đan Lô/)).toBeDefined();
  expect(within(modal).getAllByText(/Tử Xá Ma Vũ/).length).toBeGreaterThan(0);
});
