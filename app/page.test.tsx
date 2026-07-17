import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { parseItemPayload } from "@/app/lib/item-catalog";
import { summarizeItems } from "@/app/lib/wiki-search";
import itemPayload from "@/public/data/items.json";
import Loading from "./loading";
import Home from "./page";

const items = parseItemPayload(itemPayload).filter(
  (item) => item.category !== "character",
);
const summary = summarizeItems(items);

describe("item catalog page", () => {
  it("renders the non-character catalog, data summary, and primary navigation", () => {
    render(<Home />);

    expect(screen.getByText("Don't Starve Together")).toBeDefined();
    expect(
      screen.getByRole("heading", { level: 1, name: "Danh mục vật phẩm" }),
    ).toBeDefined();
    expect(
      screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }),
    ).toBeDefined();
    expect(screen.getByText(`${summary.total} vật phẩm`)).toBeDefined();
    const overview = screen.getByLabelText("Tổng quan dữ liệu");
    expect(within(overview).getByText(String(summary.total))).toBeDefined();
    expect(within(overview).getByText(String(summary.wiki))).toBeDefined();
    expect(within(overview).getByText(String(summary.recipes))).toBeDefined();
    expect(
      screen.queryByRole("heading", { level: 3, name: "abigail_attack_fx" }),
    ).toBeNull();
    expect(screen.getByRole("link", { name: "Base" }).getAttribute("href")).toBe(
      "/base",
    );
    expect(screen.queryByText(/entries$/i)).toBeNull();
  });
});

describe("item catalog loading shell", () => {
  it("announces loading and reserves four card positions", () => {
    render(<Loading />);

    expect(screen.getByRole("status").textContent).toContain(
      "Đang tải danh mục vật phẩm",
    );
    expect(screen.getAllByTestId("item-card-skeleton")).toHaveLength(4);
  });
});
