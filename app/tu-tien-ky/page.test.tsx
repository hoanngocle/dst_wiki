import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";

import TuTienKyPage from "./page";

it("registers the expanded mod catalog and preserves search and detail navigation", () => {
  render(<TuTienKyPage />);
  expect(screen.getByRole("heading", { level: 1, name: "Phàm Nhân Tu Tiên" })).toBeDefined();
  expect(screen.getAllByRole("button", { name: /^Xem chi tiết / }).length).toBeGreaterThan(3);
  for (const name of ["Truyền Tống Trận", "Lục Mạch Thần Kiếm", "Cam Tỉnh", "Chậu Hoa Uẩn Linh"]) {
    expect(screen.getByRole("button", { name: `Xem chi tiết ${name}` })).toBeDefined();
  }

  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), {
    target: { value: "truyen tong" },
  });
  // The integrated Cổ Trận skin is searchable alongside its base portal.
  expect(screen.getAllByRole("button", { name: /^Xem chi tiết / })).toHaveLength(2);
  fireEvent.click(screen.getByRole("button", { name: "Xem chi tiết Truyền Tống Trận" }));
  const dialog = screen.getByRole("dialog", { name: "Truyền Tống Trận" });
  expect(within(dialog).getByText(/dịch chuyển nhanh/)).toBeDefined();
  fireEvent.click(within(dialog).getByRole("button", { name: "Đóng chi tiết" }));

  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." }), {
    target: { value: "EVA" },
  });
  expect(screen.getByLabelText("Loại: Nhân vật")).toBeDefined();
  fireEvent.click(screen.getByRole("button", { name: "Xem chi tiết EVA" }));
  expect(screen.getByRole("dialog", { name: "EVA" })).toBeDefined();
});
