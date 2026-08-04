import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import CharactersPage from "./page";

describe("character catalog page", () => {
  it("builds exactly 28 complete curated profiles with Tu Tiên first", () => {
    render(<CharactersPage />);

    expect(
      screen.getAllByRole("button", { name: /^Mở hồ sơ / }),
    ).toHaveLength(28);
    expect(screen.getByTestId("character-total").textContent).toBe("28");
    expect(screen.getByTestId("character-tu-tien-total").textContent).toBe("9");
    expect(screen.getByTestId("character-dst-total").textContent).toBe("19");
    const grid = screen.getByTestId("character-grid");
    expect(
      within(grid).getAllByRole("button", { name: /^Mở hồ sơ / })[0].getAttribute(
        "aria-label",
      ),
    ).toMatch(/^Mở hồ sơ (Hàn Thiên Tôn|Lạc Thần)/);
  });

  it("does not expose evidence or legacy DST detail routes in rendered HTML", () => {
    const { container } = render(<CharactersPage />);

    expect(container.innerHTML).not.toContain("evidence");
    expect(container.innerHTML).not.toContain("/dst/items");
    expect(container.querySelector('[href="/dst/characters"]')).toBeNull();
    expect(container.querySelector('[href^="/dst"], [src^="/dst"]')).toBeNull();
  });
});
