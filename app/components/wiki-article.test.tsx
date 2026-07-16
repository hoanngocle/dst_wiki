import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { WikiArticle } from "./wiki-article";

const detail = {
  schema_version: 1,
  pageId: 100736,
  title: "Halberd",
  canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd",
  html: "<h2>Halberd</h2><p>Pointy and hurty.</p>",
  categories: ["Items"],
  images: [
    {
      title: "File:Halberd.png",
      src: "/assets/wiki/halberd.png",
      mime: "image/png",
      width: 64,
      height: 64,
    },
  ],
  recipes: [],
  revision: {
    id: 569319,
    sha1: "5bf67f6c77b1a0d0c5bb66b0ef02ccf5c04dba64",
    timestamp: "2026-07-12T08:43:43Z",
  },
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("WikiArticle", () => {
  it("shows a loading state while the local article request is pending", () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise(() => undefined)));

    render(
      <WikiArticle
        detailUrl="/data/wiki/pages/100736.json"
        canonicalUrl={detail.canonicalUrl}
      />,
    );

    expect(screen.getByRole("status").textContent).toContain(
      "Đang tải bài viết Wiki",
    );
  });

  it("renders validated local article HTML and its canonical link", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, json: async () => detail }),
    );

    render(
      <WikiArticle
        detailUrl="/data/wiki/pages/100736.json"
        canonicalUrl={detail.canonicalUrl}
      />,
    );

    expect(await screen.findByText("Pointy and hurty.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Halberd" })).toBeDefined();
    expect(screen.getByRole("img", { name: "File:Halberd.png" })).toHaveProperty(
      "src",
      "http://localhost:3000/assets/wiki/halberd.png",
    );
    expect(
      screen.getByRole("link", { name: "Mở trên Don't Starve Wiki" }),
    ).toHaveProperty("href", detail.canonicalUrl);
  });

  it("keeps the external source available and retries a failed local request", async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new Error("offline"))
      .mockResolvedValueOnce({ ok: true, json: async () => detail });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <WikiArticle
        detailUrl="/data/wiki/pages/100736.json"
        canonicalUrl={detail.canonicalUrl}
      />,
    );

    expect(await screen.findByText("Không tải được bài viết Wiki")).toBeDefined();
    expect(
      screen.getByRole("link", { name: "Mở trên Don't Starve Wiki" }),
    ).toHaveProperty("href", detail.canonicalUrl);

    fireEvent.click(screen.getByRole("button", { name: "Thử lại" }));

    expect(await screen.findByText("Pointy and hurty.")).toBeDefined();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("renders normalized Wiki regions before the remaining article", async () => {
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
    const onSelectItem = vi.fn();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          ...detail,
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
                  quantity: "1-3",
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
                    entityId: "base_game:nightlight",
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
      <WikiArticle
        detailUrl="/data/wiki/pages/100736.json"
        canonicalUrl={detail.canonicalUrl}
        itemsById={new Map([[nightLight.id, nightLight]])}
        onSelectItem={onSelectItem}
      />,
    );

    const dropHeading = await screen.findByRole("heading", { name: "Drop table" });
    const articleHeading = screen.getByRole("heading", { name: "Halberd" });
    expect(
      dropHeading.compareDocumentPosition(articleHeading) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Đèn bóng đêm" }));
    expect(onSelectItem).toHaveBeenCalledWith(nightLight);
  });
});
