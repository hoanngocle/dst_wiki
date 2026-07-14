import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Loading from "./loading";
import Home from "./page";

describe("Items page", () => {
  it("renders the real Vietnamese item catalog", () => {
    render(<Home />);

    expect(screen.getByText("Don't Starve Together")).toBeDefined();
    expect(
      screen.getByRole("heading", { level: 1, name: "Tra cứu vật phẩm" }),
    ).toBeDefined();
    expect(
      screen.getByRole("searchbox", { name: "Tìm kiếm Items." }),
    ).toBeDefined();
    expect(screen.getAllByText("437 Items").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Bò Lai")).toBeDefined();
  });

  it("hides the header item count below the 768px breakpoint", () => {
    render(<Home />);
    const itemCount = screen
      .getAllByText("437 Items")
      .find((element) => element.closest("header"));

    expect(itemCount).toBeDefined();
    expect(itemCount?.className.split(/\s+/)).toContain("md:block");
    expect(itemCount?.className.split(/\s+/)).not.toContain("sm:block");
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
