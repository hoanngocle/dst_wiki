import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { PhamNhanGuides } from "./pham-nhan-guides";

it("searches copied guides and keeps reward tables readable", () => {
  render(<PhamNhanGuides />);
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm hướng dẫn" }), { target: { value: "May Quay Thuong" } });
  expect(screen.getByRole("status").textContent).toBe("1 chủ đề");
  fireEvent.click(screen.getByText("Máy Quay Thưởng · Bảng thưởng"));
  expect(screen.getAllByRole("table").length).toBeGreaterThan(0);
  expect(screen.getByRole("link", { name: /Xem Wiki kỹ năng/ }).getAttribute("href")).toBe("/solo-leveling");
});
