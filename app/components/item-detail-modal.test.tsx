import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

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
  wiki: null,
};

const wikiItem: ItemListEntry = {
  id: "wiki:100736",
  prefabId: "wiki-100736",
  namespace: "base_game",
  category: "item",
  name: "Halberd",
  englishName: "Halberd",
  description: "Pointy and hurty.",
  craftingNote: null,
  sprite: null,
  recipe: null,
  wiki: {
    pageId: 100736,
    title: "Halberd",
    canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd",
    categories: ["Items"],
    mappingState: "unmatched",
    detailUrl: "/data/wiki/pages/100736.json",
    relatedPages: [
      {
        pageId: 100737,
        title: "Halberd/DST",
        canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd/DST",
        detailUrl: "/data/wiki/pages/100737.json",
      },
    ],
  },
};

const nightLight: ItemListEntry = {
  id: "base_game:nightlight",
  prefabId: "nightlight",
  namespace: "base_game",
  category: "structure",
  name: "Đèn bóng đêm",
  englishName: "Night Light",
  description: null,
  craftingNote: null,
  sprite: null,
  recipe: null,
  wiki: null,
};

function modalProps(selectedItem: ItemListEntry) {
  return {
    item: selectedItem,
    itemsById: new Map([[nightLight.id, nightLight]]),
    onSelectItem: vi.fn(),
    onClose: vi.fn(),
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("ItemDetailModal", () => {
  it("renders full item details and focuses the close button", () => {
    render(<ItemDetailModal {...modalProps(item)} />);

    const dialog = screen.getByRole("dialog", { name: "Vàng" });
    expect(dialog).toBeDefined();
    expect(dialog.className).not.toContain("overflow-y-auto");
    expect(dialog.className).not.toContain("max-h-");
    expect(dialog.parentElement?.className).toContain("overflow-y-auto");
    expect(screen.getByText("Gold Nugget")).toBeDefined();
    expect(screen.queryByText("goldnugget")).toBeNull();
    expect(screen.getByLabelText("Đá, số lượng 1")).toBeDefined();
    expect(screen.getByText("Item")).toBeDefined();
    expect(screen.getByText("DST")).toBeDefined();
    expect(screen.queryByText("DST gốc liên quan")).toBeNull();
    expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
    expect(screen.getByText("=")).toBeDefined();
    expect(screen.getByLabelText("Kết quả: Vàng, số lượng 1")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Mô tả" })).toBeDefined();
    expect(screen.getByText("Một cục vàng.")).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Source" })).toBeNull();
    expect(screen.queryByText("Dropped by")).toBeNull();
    expect(screen.queryByRole("heading", { name: "Thông tin kỹ thuật" })).toBeNull();
    expect(screen.queryByText("Prefab ID")).toBeNull();
    expect(screen.queryByRole("heading", { name: "Object Info" })).toBeNull();
    const close = screen.getByRole("button", { name: "Đóng chi tiết" });
    expect(close.className).toContain("cursor-pointer");
    expect(document.activeElement).toBe(close);
  });

  it("closes from the close button and Escape", () => {
    const onClose = vi.fn();
    render(<ItemDetailModal {...modalProps(item)} onClose={onClose} />);

    fireEvent.click(screen.getByRole("button", { name: "Đóng chi tiết" }));
    fireEvent.keyDown(document, { key: "Escape" });

    expect(onClose).toHaveBeenCalledTimes(2);
  });

  it("closes only when the backdrop itself is clicked", () => {
    const onClose = vi.fn();
    render(<ItemDetailModal {...modalProps(item)} onClose={onClose} />);

    const dialog = screen.getByRole("dialog", { name: "Vàng" });
    const backdrop = dialog.parentElement as HTMLElement;
    fireEvent.click(dialog);
    expect(onClose).not.toHaveBeenCalled();

    fireEvent.click(backdrop);
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("keeps keyboard focus inside the modal", () => {
    render(<ItemDetailModal {...modalProps(item)} />);

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

    const { unmount } = render(<ItemDetailModal {...modalProps(item)} />);
    expect(document.body.style.overflow).toBe("hidden");

    unmount();
    expect(document.activeElement).toBe(opener);
    expect(document.body.style.overflow).toBe(previousOverflow);
    opener.remove();
  });

  it("omits the recipe panel when no recipe exists", () => {
    render(
      <ItemDetailModal
        {...modalProps(item)}
        item={{ ...item, description: null, recipe: null }}
      />,
    );

    expect(screen.queryByRole("heading", { name: "Công thức" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Thông tin kỹ thuật" })).toBeNull();
  });

  it("shows a crafting note inside the runtime recipe panel", () => {
    render(
      <ItemDetailModal
        {...modalProps(item)}
        item={{ ...item, craftingNote: "Rèn bằng linh lực tinh khiết." }}
      />,
    );

    expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
    expect(screen.getByText("Rèn bằng linh lực tinh khiết.")).toBeDefined();
  });

  it("shows a note-only crafting panel without inventing ingredients", () => {
    render(
      <ItemDetailModal
        {...modalProps(item)}
        item={{
          ...item,
          recipe: null,
          craftingNote: "Tiêu hao 10 điểm máu để tạo ra một cánh hoa.",
        }}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Cách tạo / ghi chú chế tạo" }),
    ).toBeDefined();
    expect(screen.getByText("Tiêu hao 10 điểm máu để tạo ra một cánh hoa.")).toBeDefined();
    expect(screen.queryByText("=")).toBeNull();
  });

  it("loads a standalone wiki article without obsolete metadata panels", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          schema_version: 1,
          pageId: 100736,
          title: "Halberd",
          canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd",
          html: "<p>Full Halberd article.</p>",
          categories: ["Items"],
          images: [],
          recipes: [],
          revision: {
            id: 569319,
            sha1: "5bf67f6c77b1a0d0c5bb66b0ef02ccf5c04dba64",
            timestamp: "2026-07-12T08:43:43Z",
          },
        }),
      }),
    );

    render(<ItemDetailModal {...modalProps(wikiItem)} />);

    expect(screen.queryByText("Wiki page")).toBeNull();
    expect(screen.queryByText("100736")).toBeNull();
    expect(screen.queryByText("wiki-100736")).toBeNull();
    expect(screen.queryByRole("heading", { name: "Trang liên quan" })).toBeNull();
    expect(screen.queryByRole("link", { name: "Halberd/DST" })).toBeNull();
    expect(await screen.findByText("Full Halberd article.")).toBeDefined();
  });

  it("forwards mapped Wiki item selections to the shared detail flow", async () => {
    const onSelectItem = vi.fn();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          schema_version: 1,
          pageId: 100736,
          title: "Halberd",
          canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd",
          html: "<p>Remaining article.</p>",
          categories: ["Items"],
          images: [],
          revision: {
            id: 569319,
            sha1: "5bf67f6c77b1a0d0c5bb66b0ef02ccf5c04dba64",
            timestamp: "2026-07-12T08:43:43Z",
          },
          normalized: {
            schema_version: 1,
            dropTable: {
              rows: [
                {
                  sources: [
                    {
                      title: "Beardling",
                      url: "https://dontstarve.wiki.gg/wiki/Beardling",
                      entityId: null,
                    },
                  ],
                  quantity: "1",
                  chance: "40%",
                  context: null,
                },
              ],
            },
            usage: {
              recipes: [
                {
                  result: {
                    title: "Night Light",
                    url: "https://dontstarve.wiki.gg/wiki/Night_Light",
                    entityId: nightLight.id,
                  },
                  resultAmount: 1,
                  nightmareFuelAmount: 2,
                  ingredients: [],
                  station: "Prestihatitator",
                  dlc: null,
                  character: null,
                  note: null,
                },
              ],
            },
          },
        }),
      }),
    );

    render(
      <ItemDetailModal
        {...modalProps(wikiItem)}
        onSelectItem={onSelectItem}
      />,
    );

    fireEvent.click(
      await screen.findByRole("button", { name: "Đèn bóng đêm, số lượng 1" }),
    );
    expect(onSelectItem).toHaveBeenCalledWith(nightLight);
  });
});
