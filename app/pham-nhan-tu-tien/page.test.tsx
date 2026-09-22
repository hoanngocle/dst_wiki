import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import Page from "./page";
import nextConfig from "@/next.config";

it("renders the generated runtime snapshot instead of legacy Solo data", () => {
  render(<Page />);
  expect(screen.getByRole("heading", { name: "Phàm Nhân Tu Tiên" })).toBeDefined();
  expect(screen.getByRole("button", { name: "Vật phẩm" })).toBeDefined();
  expect(screen.getByRole("link", { name: "Tiến trình" }).getAttribute("href")).toBe(
    "/pham-nhan-tu-tien/tien-trinh",
  );
  expect(screen.queryByRole("link", { name: "Config" })).toBeNull();
});

it("does not keep a tu-tien-ky redirect", async () => {
  expect(await nextConfig.redirects?.()).toBeUndefined();
});
