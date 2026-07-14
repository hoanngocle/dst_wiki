import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { ItemDetailModal } from "./item-detail-modal";

const item: ItemListEntry = {
  id: "base_game:goldnugget",
  prefabId: "goldnugget",
  namespace: "base_game",
  name: "Vàng",
  englishName: "Gold Nugget",
  description: "Một cục vàng.",
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

    expect(screen.getByRole("dialog", { name: "Chi tiết Vàng" })).toBeDefined();
    expect(screen.getByText("Gold Nugget")).toBeDefined();
    expect(screen.getByText("goldnugget")).toBeDefined();
    expect(screen.getByText("Một cục vàng.")).toBeDefined();
    expect(screen.getByLabelText("Đá, số lượng 1")).toBeDefined();
    expect(document.activeElement).toBe(
      screen.getByRole("button", { name: "Đóng chi tiết" }),
    );
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

    const dialog = screen.getByRole("dialog", { name: "Chi tiết Vàng" });
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
});
