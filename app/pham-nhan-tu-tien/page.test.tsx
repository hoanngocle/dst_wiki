import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import Page from "./page";
import nextConfig from "@/next.config";
import { tuTienKyItems } from "@/app/data/tu-tien-ky";
import { tuTienKyVersion } from "@/app/data/tu-tien-ky";

it("reflects integrated EVA, nine bosses and blueprint-locked armor", () => {
  expect(tuTienKyVersion).toBe("2.0.3");
  expect(tuTienKyItems.filter((item) => item.category === "boss")).toHaveLength(9);
  expect(tuTienKyItems.some((item) => item.prefabId === "calliope_mori")).toBe(false);
  expect(tuTienKyItems.find((item) => item.prefabId === "eva")?.description).toContain("Achievement & Level");
  const armor = tuTienKyItems.find((item) => item.prefabId === "ttk_xshj")!;
  expect(armor.craftingNote).toContain("học bản vẽ");
  expect(armor.recipe?.ingredients[0].id).toBe("tu_tien_ky:ttk_boss_mgqg");
  expect(tuTienKyItems.find((item) => item.prefabId === "ttk_boss_back_xh")?.description).toContain("18 ô");
});

it("preserves old links with an exact redirect without redirecting image assets", async () => {
  expect(await nextConfig.redirects!()).toContainEqual({ source: "/tu-tien-ky", destination: "/pham-nhan-tu-tien", permanent: true });
});

it("exposes Config and lets users open newly integrated content", () => {
  render(<Page />);
  expect(screen.getByRole("link", { name: "Config" }).getAttribute("href")).toBe("/pham-nhan-tu-tien/config");
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), { target: { value: "Linh Tuyền Cực Phẩm" } });
  fireEvent.click(screen.getByRole("button", { name: "Xem chi tiết Linh Tuyền Cực Phẩm" }));
  expect(screen.getByRole("dialog", { name: "Linh Tuyền Cực Phẩm" })).toBeDefined();
});

it("includes the copied features and removes the obsolete optional Solo claim", () => {
  for (const code of ["ttk_fsct", "ttk_choujiangji", "ttk_chuongthienbinh", "ttk_spirit_workshop", "ttk_zcmj", "ttk_xshj", "heat_star", "ttk_rock3"]) {
    expect(tuTienKyItems.some((item) => item.prefabId === code)).toBe(true);
  }
  expect(JSON.stringify(tuTienKyItems)).not.toContain("Solo là tùy chọn");
});
