import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Page from "./page";

describe("HotKeyPage", () => {
  it("presents the current Pham Nhan hotkeys in scannable groups", () => {
    render(<Page />);

    expect(
      screen.getByRole("heading", { level: 1, name: "Hướng dẫn hotkey" }),
    ).toBeDefined();
    expect(screen.getByRole("heading", { name: "Giao diện và kho đồ" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Kỹ năng EVA" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Chiến đấu và tương tác" })).toBeDefined();
    expect(screen.getByText("Mở Bảng Tổng Hợp")).toBeDefined();
    expect(screen.getByText("Sinh Chi Hoa")).toBeDefined();
    expect(screen.getByText("Ra lệnh Fruit Fly Bóng Ma")).toBeDefined();
  });

  it("reveals usage notes when a hotkey item is pressed", () => {
    render(<Page />);

    const summary = screen.getByText("Mở cửa hàng hầm ngục").closest("summary");
    const details = summary?.closest("details");

    expect(summary).not.toBeNull();
    expect(details?.open).toBe(false);

    fireEvent.click(summary!);

    expect(details?.open).toBe(true);
    expect(
      screen.getByText("Chỉ dùng khi nhân vật còn sống, đang ở mặt đất và không mở bảng hướng dẫn."),
    ).toBeDefined();
  });

  it("links the hotkey guide from the Pham Nhan section navigation", () => {
    render(<Page />);

    const link = screen.getByRole("link", { name: "Hotkey" });
    expect(link.getAttribute("href")).toBe("/hot-key");
    expect(link.getAttribute("aria-current")).toBe("page");
  });

  it("keeps runtime-sensitive combinations and targeting instructions accurate", () => {
    render(<Page />);

    expect(screen.getByLabelText("Alt cộng Chuột phải")).toBeDefined();
    expect(screen.getByText("Khóa vật phẩm trong Kho Quân Vương")).toBeDefined();
    expect(screen.queryByLabelText("Shift cộng Chuột phải")).toBeNull();
    expect(screen.getAllByText(/sau đó chọn vị trí thi triển/i)).toHaveLength(3);
  });
});
