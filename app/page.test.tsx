import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Loading from "./loading";
import Home from "./page";

describe("Prefabs page", () => {
  it("renders the complete prefab catalog and primary navigation", () => {
    render(<Home />);

    expect(screen.getByText("Don't Starve Together")).toBeDefined();
    expect(
      screen.getByRole("heading", { level: 1, name: "Tra cứu Prefab" }),
    ).toBeDefined();
    expect(
      screen.getByRole("searchbox", { name: "Tìm kiếm Prefabs." }),
    ).toBeDefined();
    expect(screen.getByText("1975 Prefabs")).toBeDefined();
    expect(
      screen.getByRole("heading", { level: 3, name: "abigail_attack_fx" }),
    ).toBeDefined();
    expect(screen.getByRole("link", { name: "Base" }).getAttribute("href")).toBe(
      "/base",
    );
    expect(screen.queryByText(/entries$/i)).toBeNull();
  });
});

describe("Prefabs page loading shell", () => {
  it("announces loading and reserves four card positions", () => {
    render(<Loading />);

    expect(screen.getByRole("status").textContent).toContain(
      "Đang tải danh sách Prefabs",
    );
    expect(screen.getAllByTestId("item-card-skeleton")).toHaveLength(4);
  });
});
