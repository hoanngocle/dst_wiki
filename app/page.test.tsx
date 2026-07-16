import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { parseItemPayload } from "@/app/lib/item-catalog";
import itemPayload from "@/public/data/items.json";
import Loading from "./loading";
import Home from "./page";

const itemCount = parseItemPayload(itemPayload).length;

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
    expect(screen.getByText(`${itemCount} Prefabs`)).toBeDefined();
    expect(
      screen.queryByRole("heading", { level: 3, name: "abigail_attack_fx" }),
    ).toBeNull();
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
