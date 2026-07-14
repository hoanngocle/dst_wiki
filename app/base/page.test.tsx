import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import BasePage from "./page";

it("renders six named base image cards", () => {
  render(<BasePage />);
  expect(screen.getByRole("heading", { level: 1, name: "Thư viện Base" })).toBeDefined();
  expect(screen.getByRole("link", { name: "Base" }).getAttribute("aria-current")).toBe("page");
  expect(screen.getAllByRole("img")).toHaveLength(6);
  expect(screen.getAllByRole("listitem")).toHaveLength(6);
  expect(screen.getByText("Base Khởi Đầu")).toBeDefined();
});
