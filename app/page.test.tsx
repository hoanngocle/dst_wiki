import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Loading from "./loading";
import Home from "./page";

describe("Items page", () => {
  it("renders the real Vietnamese item catalog and primary navigation", () => {
    render(<Home />);

    expect(screen.getByText("Don't Starve Together")).toBeDefined();
    expect(
      screen.getByRole("heading", { level: 1, name: "Tra cứu vật phẩm" }),
    ).toBeDefined();
    expect(
      screen.getByRole("searchbox", { name: "Tìm kiếm Items." }),
    ).toBeDefined();
    expect(screen.getByText("437 Items")).toBeDefined();
    expect(screen.getByText("Bò Lai")).toBeDefined();
    expect(screen.getByRole("link", { name: "Base" }).getAttribute("href")).toBe(
      "/base",
    );
    expect(screen.queryByText(/entries$/i)).toBeNull();
  });
});

describe("Items page loading shell", () => {
  it("announces loading and reserves four card positions", () => {
    render(<Loading />);

    expect(screen.getByRole("status").textContent).toContain(
      "Đang tải danh sách Items",
    );
    expect(screen.getAllByTestId("item-card-skeleton")).toHaveLength(4);
  });
});
