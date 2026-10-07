import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import Page from "./page";
import nextConfig from "@/next.config";

it("publishes the NOVA runtime snapshot at the canonical route", () => {
  render(<Page />);
  expect(screen.getByRole("heading", { name: "NOVA" })).toBeDefined();
  expect(screen.getByRole("button", { name: "Vật phẩm" })).toBeDefined();
  expect(screen.getByRole("link", { name: "Tiến trình" }).getAttribute("href")).toBe(
    "/nova/tien-trinh",
  );
  expect(screen.queryByRole("link", { name: "Config" })).toBeNull();
});

it("keeps the hot-key redirect after removing the Pham Nhan routes", async () => {
  expect(await nextConfig.redirects?.()).toEqual([
    { source: "/hot-key", destination: "/nova/hot-key", permanent: true },
  ]);
});
