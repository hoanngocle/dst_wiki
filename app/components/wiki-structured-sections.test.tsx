import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import type { NormalizedWikiSections } from "@/app/lib/wiki-detail";
import { WikiStructuredSections } from "./wiki-structured-sections";


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

const sections: NormalizedWikiSections = {
  dropTable: {
    rows: Array.from({ length: 10 }, (_, index) => ({
      sources: [
        {
          title: index === 0 ? "Beardling" : `Source ${index + 1}`,
          url:
            index === 0
              ? "https://dontstarve.wiki.gg/wiki/Beardling"
              : `https://dontstarve.wiki.gg/wiki/Source_${index + 1}`,
          entityId: null,
        },
      ],
      quantity: index === 0 ? "1-3" : "1",
      chance: index === 0 ? "40%" : "100%",
      context: index === 0 ? "Khi mất trí" : null,
    })),
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
        ingredients: [
          {
            item: {
              title: "Gold Nugget",
              url: "https://dontstarve.wiki.gg/wiki/Gold_Nugget",
              entityId: null,
            },
            amount: 8,
          },
        ],
        station: "Prestihatitator",
        dlc: null,
        character: null,
        note: null,
      },
      {
        result: {
          title: "Dripple Pipes",
          url: "https://dontstarve.wiki.gg/wiki/Dripple_Pipes",
          entityId: null,
        },
        resultAmount: 1,
        nightmareFuelAmount: 2,
        ingredients: [],
        station: "Prestihatitator",
        dlc: "Shipwrecked",
        character: "Warly",
        note: "Chỉ dùng trong DLC.",
      },
    ],
  },
};

describe("WikiStructuredSections", () => {
  it("renders complete Drop and Usage regions with Wiki facts", () => {
    render(
      <WikiStructuredSections
        sections={sections}
        itemsById={new Map([[nightLight.id, nightLight]])}
        onSelectItem={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "Drop table" })).toBeDefined();
    expect(screen.getByText("10 nguồn từ Wiki")).toBeDefined();
    expect(screen.getByText("1-3")).toBeDefined();
    expect(screen.getByText("40%")).toBeDefined();
    expect(screen.getByText("Khi mất trí")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Usage" })).toBeDefined();
    expect(screen.getByText("2 công thức từ Wiki")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Don't Starve" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Shipwrecked" })).toBeDefined();
    expect(screen.getAllByText("Prestihatitator")).toHaveLength(2);
    expect(screen.getByText("Warly")).toBeDefined();
    expect(screen.getByText("Chỉ dùng trong DLC.")).toBeDefined();
    expect(screen.getByRole("link", { name: "Beardling" })).toHaveProperty(
      "href",
      "https://dontstarve.wiki.gg/wiki/Beardling",
    );
    expect(screen.getByRole("link", { name: "Gold Nugget" })).toBeDefined();
  });

  it("opens a resolved catalog item inside the current detail flow", () => {
    const onSelectItem = vi.fn();
    render(
      <WikiStructuredSections
        sections={sections}
        itemsById={new Map([[nightLight.id, nightLight]])}
        onSelectItem={onSelectItem}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Đèn bóng đêm" }));

    expect(onSelectItem).toHaveBeenCalledWith(nightLight);
  });
});
