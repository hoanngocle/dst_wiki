import { render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";

import CultivationGuidePage from "./page";

it("renders the dedicated cultivation table from the static item catalog", () => {
  render(<CultivationGuidePage />);

  expect(screen.getByRole("link", { name: "Cảnh giới Tu Tiên" }).getAttribute("aria-current")).toBe(
    "page",
  );
  expect(screen.queryByRole("link", { name: /Trở lại thư viện Guide/ })).toBeNull();
  const table = screen.getByRole("table", { name: "Thứ tự cảnh giới Tu Tiên" });
  expect(within(table).getAllByRole("row")).toHaveLength(16);
  expect(
    within(table).getByRole("row", { name: /Cảnh giới 15: Hóa Thần Hậu Kỳ → Phản Hư Sơ Kỳ/ }),
  ).toBeDefined();
  const sprites = within(table).getAllByTestId("static-game-sprite");
  expect(sprites.length).toBeGreaterThan(15);
  expect(sprites[0].style.backgroundImage).toContain("/assets/game/");
});
