import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { parseWikiPageDetail } from "@/app/lib/wiki-detail";
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

describe("WikiArticle", () => {
  it("renders validated local article HTML and its canonical link", () => {
    render(<WikiArticle detail={parseWikiPageDetail(detail)} />);

    expect(screen.getByText("Pointy and hurty.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Halberd" })).toBeDefined();
    expect(screen.getByRole("img", { name: "File:Halberd.png" })).toHaveProperty(
      "src",
      "http://localhost:3000/assets/wiki/halberd.png",
    );
    const gallery = screen.getByRole("region", { name: "Gallery" });
    expect(gallery.querySelector("[data-gallery-grid]")?.className).toContain("grid");
    const galleryItem = screen.getByRole("figure", { name: "Halberd.png" });
    expect(galleryItem.className).toContain("group");
    expect(galleryItem.tabIndex).toBe(0);
    const caption = screen.getByText("Halberd.png");
    expect(caption.className).toContain("opacity-0");
    expect(caption.className).toContain("group-hover:opacity-100");
    expect(caption.className).toContain("group-focus-visible:opacity-100");
    expect(
      screen.getByRole("link", { name: "Mở trên Don't Starve Wiki" }),
    ).toHaveProperty("href", detail.canonicalUrl);
  });

  it("prefers a concise Vietnamese summary over the raw Wiki article", () => {
    render(
      <WikiArticle
        detail={parseWikiPageDetail({
          ...detail,
          summaryViHtml:
            "<h2>Tóm tắt</h2><p>Nhiên liệu dùng cho ma thuật bóng tối.</p>",
        })}
      />,
    );

    expect(screen.getByRole("heading", { name: "Tóm tắt" })).toBeDefined();
    expect(screen.getByText("Nhiên liệu dùng cho ma thuật bóng tối.")).toBeDefined();
    expect(screen.queryByText("Pointy and hurty.")).toBeNull();
  });

  it("renders normalized Wiki regions before the remaining article", () => {
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
    const normalizedDetail = parseWikiPageDetail({
      ...detail,
      normalized: {
        schema_version: 2,
        subject: {
          title: "Nightmare Fuel",
          url: "https://dontstarve.wiki.gg/wiki/Nightmare_Fuel",
          entityId: null,
        },
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
              subjectAmount: 2,
              ingredients: [],
              station: "Prestihatitator",
              dlc: null,
              character: null,
              note: null,
            },
          ],
        },
      },
    });

    render(
      <WikiArticle
        detail={normalizedDetail}
        itemsById={new Map([[nightLight.id, nightLight]])}
        onSelectItem={onSelectItem}
      />,
    );

    const dropHeading = screen.getByRole("heading", { name: "Drop table" });
    const articleHeading = screen.getByRole("heading", { name: "Halberd" });
    expect(
      dropHeading.compareDocumentPosition(articleHeading) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    fireEvent.click(
      screen.getByRole("button", { name: "Đèn bóng đêm, số lượng 1" }),
    );
    expect(onSelectItem).toHaveBeenCalledWith(nightLight);
  });
});
