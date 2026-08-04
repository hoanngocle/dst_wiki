import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import GuidesPage from "./page";

it("lists the static library and the dedicated cultivation route using root URLs", () => {
  const { container } = render(<GuidesPage />);

  expect(screen.getByRole("heading", { level: 1, name: "Guide thực chiến, đọc riêng từng bài" })).toBeDefined();
  expect(
    screen
      .getByText("15 lần thăng cấp, đan dược và nguyên liệu tương ứng.")
      .closest("a")
      ?.getAttribute("href"),
  ).toBe("/tu-tien");
  expect(screen.getByTestId("guide-library-hero-stats").textContent).toContain(
    "Bài đã duyệt5",
  );
  expect(container.innerHTML).not.toContain("/dst/");
});
