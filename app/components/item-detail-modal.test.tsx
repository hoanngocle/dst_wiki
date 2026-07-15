import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { ItemDetailModal } from "./item-detail-modal";

const item: ItemListEntry = {
  id: "base_game:goldnugget",
  prefabId: "goldnugget",
  namespace: "base_game",
  category: "item",
  name: "Vàng",
  englishName: "Gold Nugget",
  description: "Một cục vàng.",
  craftingNote: null,
  sprite: null,
  recipe: {
    outputCount: 1,
    ingredients: [
      {
        id: "base_game:rocks",
        name: "Đá",
        amount: 1,
        sprite: null,
      },
    ],
  },
};

describe("ItemDetailModal", () => {
  it("renders full item details and focuses the close button", () => {
    render(<ItemDetailModal item={item} onClose={vi.fn()} />);

    expect(screen.getByRole("dialog", { name: "Vàng" })).toBeDefined();
    expect(screen.getByText("Gold Nugget")).toBeDefined();
    expect(screen.getByText("goldnugget")).toBeDefined();
    expect(screen.getByLabelText("Đá, số lượng 1")).toBeDefined();
    expect(screen.getByText("Item")).toBeDefined();
    expect(screen.getByText("DST gốc liên quan")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
    expect(screen.getByText("=")).toBeDefined();
    expect(screen.getByLabelText("Kết quả: Vàng, số lượng 1")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Source" })).toBeDefined();
    expect(screen.getByText("Dropped by")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Miscellaneous" })).toBeDefined();
    expect(screen.getByText("Prefab ID")).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Object Info" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Description" })).toBeNull();
    const close = screen.getByRole("button", { name: "Đóng chi tiết" });
    expect(close.className).toContain("cursor-pointer");
    expect(document.activeElement).toBe(close);
  });

  it("closes from the close button and Escape", () => {
    const onClose = vi.fn();
    render(<ItemDetailModal item={item} onClose={onClose} />);

    fireEvent.click(screen.getByRole("button", { name: "Đóng chi tiết" }));
    fireEvent.keyDown(document, { key: "Escape" });

    expect(onClose).toHaveBeenCalledTimes(2);
  });

  it("closes only when the backdrop itself is clicked", () => {
    const onClose = vi.fn();
    render(<ItemDetailModal item={item} onClose={onClose} />);

    const dialog = screen.getByRole("dialog", { name: "Vàng" });
    const backdrop = dialog.parentElement as HTMLElement;
    fireEvent.click(dialog);
    expect(onClose).not.toHaveBeenCalled();

    fireEvent.click(backdrop);
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("keeps keyboard focus inside the modal", () => {
    render(<ItemDetailModal item={item} onClose={vi.fn()} />);

    const close = screen.getByRole("button", { name: "Đóng chi tiết" });
    fireEvent.keyDown(document, { key: "Tab" });
    expect(document.activeElement).toBe(close);

    fireEvent.keyDown(document, { key: "Tab", shiftKey: true });
    expect(document.activeElement).toBe(close);
  });

  it("restores focus and body scrolling when it unmounts", () => {
    const opener = document.createElement("button");
    document.body.append(opener);
    opener.focus();
    const previousOverflow = document.body.style.overflow;

    const { unmount } = render(<ItemDetailModal item={item} onClose={vi.fn()} />);
    expect(document.body.style.overflow).toBe("hidden");

    unmount();
    expect(document.activeElement).toBe(opener);
    expect(document.body.style.overflow).toBe(previousOverflow);
    opener.remove();
  });

  it("omits the recipe panel when no recipe exists", () => {
    render(
      <ItemDetailModal
        item={{ ...item, description: null, recipe: null }}
        onClose={vi.fn()}
      />,
    );

    expect(screen.queryByRole("heading", { name: "Công thức" })).toBeNull();
    expect(screen.getByRole("heading", { name: "Miscellaneous" })).toBeDefined();
  });

  it("shows a crafting note inside the runtime recipe panel", () => {
    render(
      <ItemDetailModal
        item={{ ...item, craftingNote: "Rèn bằng linh lực tinh khiết." }}
        onClose={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
    expect(screen.getByText("Rèn bằng linh lực tinh khiết.")).toBeDefined();
  });

  it("shows a note-only crafting panel without inventing ingredients", () => {
    render(
      <ItemDetailModal
        item={{
          ...item,
          recipe: null,
          craftingNote: "Tiêu hao 10 điểm máu để tạo ra một cánh hoa.",
        }}
        onClose={vi.fn()}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Cách tạo / ghi chú chế tạo" }),
    ).toBeDefined();
    expect(screen.getByText("Tiêu hao 10 điểm máu để tạo ra một cánh hoa.")).toBeDefined();
    expect(screen.queryByText("=")).toBeNull();
  });
});
