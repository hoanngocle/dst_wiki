import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import Home from "./page";

it("renders the Vietnamese Don't Starve Together Items shell", () => {
  render(<Home />);
  expect(screen.getByText("Don't Starve Together")).toBeDefined();
  expect(screen.getByRole("heading", { level: 1, name: /Tìm nhanh/i })).toBeDefined();
  expect(screen.getByRole("searchbox", { name: "Tìm kiếm Items." })).toBeDefined();
  expect(screen.getByRole("link", { name: "Base" }).getAttribute("href")).toBe("/base");
  expect(screen.queryByText(/entries$/i)).toBeNull();
});
