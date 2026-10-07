import { fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
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
  details: null,
  wiki: null,
};

const rockItem: ItemListEntry = {
  ...item,
  id: "base_game:rocks",
  prefabId: "rocks",
  name: "Đá",
  englishName: "Rocks",
  description: "Một viên đá.",
  recipe: null,
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
  details: null,
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
  details: null,
  structureDetails: {
    origin: {
      status: "known",
      naturallySpawned: true,
      renewable: null,
      spawnCode: "nightlight",
      sources: [],
      respawn: null,
      craftable: false,
      note: "Xuất hiện tự nhiên.",
      evidence: [{ source: "public/data/catalog.json", locator: "origin" }],
    },
    construction: {
      status: "none",
      outputCount: null,
      ingredients: [],
      tech: null,
      station: null,
      restrictions: {},
      note: "Không thể chế tạo.",
      evidence: [{ source: "public/data/catalog.json", locator: "construction" }],
    },
    functions: {
      status: "unknown",
      facts: [],
      reason: "Chưa xác minh.",
      evidence: [{ source: "public/data/catalog.json", locator: "functions" }],
    },
    craftables: {
      status: "none",
      recipes: [],
      reason: null,
      evidence: [{ source: "public/data/catalog.json", locator: "craftables" }],
    },
    destruction: {
      status: "unknown",
      destroyable: null,
      tool: null,
      work: null,
      health: null,
      burnable: null,
      drops: [],
      regeneration: null,
      evidence: [{ source: "public/data/catalog.json", locator: "destruction" }],
    },
    visual: {
      status: "unknown",
      kind: null,
      sprite: null,
      image: null,
      alternatives: [],
      reason: "Chưa tìm thấy ảnh.",
      evidence: [{ source: "public/data/catalog.json", locator: "visual" }],
    },
  },
  wiki: null,
};

const tuTienItem: ItemListEntry = {
  ...nightLight,
  id: "tu_tien:unknown_relic",
  prefabId: "unknown_relic",
  namespace: "tu_tien",
  category: "item",
  name: "Bí Bảo",
  details: {
    recipeStatus: "unknown",
    usage: { status: "unknown", recipes: [], effects: [] },
    dropBy: { status: "unknown", sources: [] },
  },
};

function peekProps(selectedItem: ItemListEntry) {
  return {
    item: selectedItem,
    itemsById: new Map([[nightLight.id, nightLight]]),
    onSelectItem: vi.fn(),
    onClose: vi.fn(),
  };
}

function ModalNavigationHarness() {
  const [selectedItem, setSelectedItem] = useState(item);

  return (
    <ItemDetailModal
      item={selectedItem}
      itemsById={new Map([
        [item.id, item],
        [rockItem.id, rockItem],
      ])}
      onSelectItem={setSelectedItem}
      onClose={() => undefined}
    />
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("ItemDetailModal", () => {
  it("describes the named dialog and bounds it to the responsive viewport", () => {
    render(
      <ItemDetailModal
        item={item}
        itemsById={new Map([[item.id, item]])}
        onSelectItem={() => undefined}
        onClose={() => undefined}
      />,
    );

    const dialog = screen.getByRole("dialog", { name: "Vàng" });
    const descriptionId = dialog.getAttribute("aria-describedby");

    expect(descriptionId).toBeTruthy();
    expect(document.getElementById(descriptionId ?? "")?.textContent).toContain(
      "Chi tiết vật phẩm Vàng.",
    );
    expect(dialog.className).toContain("max-h-[calc(100dvh-2rem)]");
  });

  it("renders the Đan Dược category label", () => {
    render(
      <ItemDetailModal
        item={{ ...item, category: "pill", name: "Tụ Khí Hoàn" }}
        itemsById={new Map()}
        onClose={() => undefined}
        onSelectItem={() => undefined}
      />,
    );

    expect(screen.getByText("Đan Dược")).toBeDefined();
  });

  it("renders full item details and focuses the close button", () => {
    render(<ItemDetailModal {...peekProps(item)} />);

    const dialog = screen.getByRole("dialog", { name: "Vàng" });
    expect(dialog).toBeDefined();
    expect(dialog.getAttribute("data-placement")).toBe("center");
    expect(dialog.className).toContain("max-h-[calc(100dvh-2rem)]");
    const body = screen.getByTestId("item-detail-modal-body");
    expect(body.className).toContain("overflow-y-auto");
    expect(body.className).toContain("overscroll-contain");
    expect(screen.queryByText("Gold Nugget")).toBeNull();
    const prefabCode = screen.getByText("goldnugget");
    expect(prefabCode.tagName).toBe("CODE");

    expect(screen.getByLabelText("Đá, số lượng 1")).toBeDefined();
    expect(screen.getByText("Item")).toBeDefined();
    expect(screen.getByText("DST")).toBeDefined();
    expect(screen.queryByText("DST gốc liên quan")).toBeNull();
    expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
    expect(screen.getByText("=")).toBeDefined();
    expect(screen.getByLabelText("Kết quả: Vàng, số lượng 1")).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Tóm tắt" })).toBeNull();
    expect(screen.getAllByRole("listitem")).toHaveLength(1);
    expect(screen.queryByRole("heading", { name: "Mô tả" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Source" })).toBeNull();
    expect(screen.queryByText("Dropped by")).toBeNull();
    expect(screen.queryByRole("heading", { name: "Thông tin kỹ thuật" })).toBeNull();
    expect(screen.queryByText("Prefab ID")).toBeNull();
    expect(screen.queryByRole("heading", { name: "Object Info" })).toBeNull();
    const close = screen.getByRole("button", { name: "Đóng chi tiết" });
    expect(close.className).toContain("cursor-pointer");
    expect(document.activeElement).toBe(close);
  });

  it("replaces a base-game recipe detail with its selected ingredient", () => {
    render(<ModalNavigationHarness />);

    const ingredientButton = screen.getByRole("button", { name: "Đá, số lượng 1" });
    ingredientButton.focus();
    expect(document.activeElement).toBe(ingredientButton);
    fireEvent.click(ingredientButton);

    const dialog = screen.getByRole("dialog", { name: "Đá" });
    expect(dialog).toBeDefined();
    expect(screen.getByText("rocks").tagName).toBe("CODE");
    expect(screen.queryByRole("dialog", { name: "Vàng" })).toBeNull();
    expect(dialog.contains(document.activeElement)).toBe(true);
  });

  it("closes from the close button and Escape", () => {
    const onClose = vi.fn();
    render(<ItemDetailModal {...peekProps(item)} onClose={onClose} />);

    fireEvent.click(screen.getByRole("button", { name: "Đóng chi tiết" }));
    fireEvent.keyDown(document, { key: "Escape" });

    expect(onClose).toHaveBeenCalledTimes(2);
  });

  it("closes only when the backdrop itself is clicked", () => {
    const onClose = vi.fn();
    render(<ItemDetailModal {...peekProps(item)} onClose={onClose} />);

    const dialog = screen.getByRole("dialog", { name: "Vàng" });
    const backdrop = dialog.parentElement as HTMLElement;
    fireEvent.click(dialog);
    expect(onClose).not.toHaveBeenCalled();

    fireEvent.click(backdrop);
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("keeps keyboard focus inside the peek", () => {
    render(<ItemDetailModal {...peekProps(item)} />);

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

    const { unmount } = render(<ItemDetailModal {...peekProps(item)} />);
    expect(document.body.style.overflow).toBe("hidden");

    unmount();
    expect(document.activeElement).toBe(opener);
    expect(document.body.style.overflow).toBe(previousOverflow);
    opener.remove();
  });

  it("keeps the peek open and scrolls its body to top when item changes", () => {
    const { rerender } = render(<ItemDetailModal {...peekProps(item)} />);
    const body = screen.getByTestId("item-detail-modal-body");
    const scrollTo = vi.fn();
    Object.defineProperty(body, "scrollTo", {
      configurable: true,
      value: scrollTo,
    });

    rerender(
      <ItemDetailModal
        {...peekProps({ ...item, id: "base_game:bunnyman", name: "Bunnyman" })}
      />,
    );

    expect(screen.getByRole("dialog", { name: "Bunnyman" })).toBeDefined();
    expect(scrollTo).toHaveBeenCalledWith({ top: 0, behavior: "auto" });
  });

  it("shows acquisition in the recipe panel even without a recipe", () => {
    render(
      <ItemDetailModal
        {...peekProps(item)}
        item={{ ...item, description: null, recipe: null }}
      />,
    );

    expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Thông tin kỹ thuật" })).toBeNull();
  });

  it("groups Tu Tiên acquisition under crafting alongside Usage", () => {
    render(<ItemDetailModal {...peekProps(tuTienItem)} />);

    expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Cách Sử dụng" })).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Nguồn nhận" })).toBeNull();
    expect(screen.getAllByText("Chưa xác định từ dữ liệu mod.")).toHaveLength(2);
  });

  it("uses the complete structure renderer for structure records", () => {
    render(<ItemDetailModal {...peekProps(nightLight)} />);

    expect(screen.getByRole("heading", { name: "Xuất hiện" })).toBeDefined();
    expect(
      screen.getByRole("heading", { name: "Vật phẩm chế tạo tại công trình" }),
    ).toBeDefined();
    expect(screen.getByRole("heading", { name: "Hình ảnh" })).toBeDefined();
  });

  it("shows a crafting note inside the runtime recipe panel", () => {
    render(
      <ItemDetailModal
        {...peekProps(item)}
        item={{ ...item, craftingNote: "Rèn bằng linh lực tinh khiết." }}
      />,
    );

    expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
    expect(screen.getByText("Rèn bằng linh lực tinh khiết.")).toBeDefined();
  });

  it("shows a note-only crafting panel without inventing ingredients", () => {
    render(
      <ItemDetailModal
        {...peekProps(item)}
        item={{
          ...item,
          recipe: null,
          craftingNote: "Tiêu hao 10 điểm máu để tạo ra một cánh hoa.",
        }}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Công thức" }),
    ).toBeDefined();
    expect(screen.getByText("Tiêu hao 10 điểm máu để tạo ra một cánh hoa.")).toBeDefined();
    expect(screen.queryByText("=")).toBeNull();
  });

  it("shows usage and acquisition without an overview or Wiki article", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<ItemDetailModal {...peekProps({ ...wikiItem, recipe: item.recipe, summary: {
      usage: { status: "known", text: "Học công thức.", sources: ["test"] },
      fuel: { status: "known", text: "15 giây.", sources: ["test"] },
      recycling: { status: "not_applicable", text: null, sources: [] },
      acquisition: { status: "known", text: "Mua từ Bà Cua.", sources: ["test"] },
    } })} />);
    expect(screen.getAllByRole("listitem")).toHaveLength(1);
    expect(screen.queryByText("Cách sử dụng:")).toBeNull();
    expect(screen.getByText("Học công thức.", { exact: false })).toBeDefined();
    expect(screen.queryByText("Giá trị nhiên liệu:")).toBeNull();
    expect(screen.queryByText("Tái chế:")).toBeNull();
    expect(screen.getByText("Mua từ Bà Cua.")).toBeDefined();
    expect(screen.queryByText("Pointy and hurty.")).toBeNull();
    expect(screen.getByText("Học công thức.", { exact: false }).closest("section")?.textContent).toContain("Cách Sử dụng");
    expect(screen.getByText("Mua từ Bà Cua.").closest("section")?.textContent).toContain("Công thức");
    expect(screen.queryByText("Bài viết Wiki")).toBeNull();
    expect(screen.queryByRole("region", { name: "Gallery" })).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.queryByRole("heading", { name: "Tóm tắt" })).toBeNull();
    expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
  });
});
