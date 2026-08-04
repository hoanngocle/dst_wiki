import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import { DstField, dstControlClassName } from "./dst-field";
import { DstHero } from "./dst-hero";
import { DstPageShell } from "./dst-page-shell";
import { DstPanel } from "./dst-panel";
import { DstState } from "./dst-state";

it("composes the shared dark DST page system", () => {
  render(
    <DstPageShell>
      <DstHero
        eyebrow="DST"
        title="Danh mục"
        description="Tra cứu dữ liệu."
        stats={[{ label: "Vật phẩm", value: 12 }]}
      />
      <DstPanel testId="filters">
        <DstField label="Tìm" htmlFor="query">
          <input id="query" className={dstControlClassName} />
        </DstField>
      </DstPanel>
      <DstState
        tone="empty"
        title="Không có dữ liệu"
        description="Hãy đổi bộ lọc."
      />
    </DstPageShell>,
  );

  expect(screen.getByTestId("dst-page-shell").className).toContain("text-nova-text");
  expect(screen.getByTestId("filters").className).toContain("bg-nova-surface");
  expect(screen.getByLabelText("Tìm").className).toContain("bg-nova-surface-soft");
  expect(screen.getByRole("heading", { name: "Danh mục" })).toBeDefined();
  expect(screen.getByText("Không có dữ liệu")).toBeDefined();
});

it("places content hero statistics beside the copy on large screens", () => {
  render(
    <DstHero
      testId="guide-hero"
      eyebrow="Sổ tay DST"
      title="Guide thực chiến"
      description="Các bài hướng dẫn."
      stats={[
        { label: "Bài lưu trữ", value: 106 },
        { label: "Phạm vi", value: "4 nhãn" },
      ]}
    />,
  );

  expect(screen.getByTestId("guide-hero-layout").className).toContain(
    "lg:grid-cols-[minmax(0,1fr)_minmax(18rem,auto)]",
  );
  expect(screen.getByTestId("guide-hero-stats").className).toContain("sm:grid-cols-2");
  expect(screen.getByTestId("guide-hero-stats").tagName).toBe("DL");
});

it("uses an alert role only for danger states", () => {
  const { rerender } = render(<DstState tone="loading" title="Đang tải dữ liệu" />);

  expect(screen.getByRole("status")).toBeDefined();
  expect(screen.queryByRole("alert")).toBeNull();

  rerender(<DstState tone="danger" title="Không thể tải dữ liệu" />);

  expect(screen.getByRole("alert").className).toContain("border-nova-danger/40");
  expect(screen.queryByRole("status")).toBeNull();
});
