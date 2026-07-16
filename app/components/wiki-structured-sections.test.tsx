import { fireEvent, render, screen, within } from "@testing-library/react";
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
  sprite: {
    src: "/assets/wiki/night-light.png",
    uv: { u1: 0, u2: 1, v1: 0, v2: 1 },
  },
  recipe: null,
  wiki: null,
};

const nightmareFuel: ItemListEntry = {
  id: "base_game:nightmarefuel",
  prefabId: "nightmarefuel",
  namespace: "base_game",
  category: "item",
  name: "Nhiên liệu Ác Mộng",
  englishName: "Nightmare Fuel",
  description: null,
  craftingNote: null,
  sprite: {
    src: "/assets/game/nightmare-fuel.png",
    uv: { u1: 0, u2: 1, v1: 0, v2: 1 },
  },
  recipe: null,
  wiki: null,
};

const catalogItems = new Map([
  [nightLight.id, nightLight],
  [nightmareFuel.id, nightmareFuel],
]);

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
          iconUrl:
            index === 0
              ? "https://dontstarve.wiki.gg/wiki/Special:Redirect/file/Beardling.png"
              : null,
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
        station: "Broken Pseudoscience Station",
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
      {
        result: {
          title: "Dark Sword",
          url: "https://dontstarve.wiki.gg/wiki/Dark_Sword",
          entityId: null,
        },
        resultAmount: 1,
        nightmareFuelAmount: 5,
        ingredients: [],
        station: "Shadow Manipulator",
        dlc: "Hamlet",
        character: null,
        note: "Chỉ dùng trong Hamlet.",
      },
      {
        result: {
          title: "Seaworthy",
          url: "https://dontstarve.wiki.gg/wiki/Seaworthy",
          entityId: null,
        },
        resultAmount: 1,
        nightmareFuelAmount: 4,
        ingredients: [],
        station: "Shadow Manipulator",
        dlc: null,
        character: null,
        note: "Only available in the world linked with a Shipwrecked world.",
      },
      {
        result: {
          title: "Skyworthy",
          url: "https://dontstarve.wiki.gg/wiki/Skyworthy",
          entityId: null,
        },
        resultAmount: 1,
        nightmareFuelAmount: 4,
        ingredients: [],
        station: "Shadow Manipulator",
        dlc: null,
        character: null,
        note: "Only available in the world linked with a Hamlet world.",
      },
    ],
  },
};

describe("WikiStructuredSections", () => {
  it("renders complete Drop and Usage regions with Wiki facts", () => {
    render(
      <WikiStructuredSections
        sections={sections}
        itemsById={catalogItems}
        onSelectItem={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "Drop table" })).toBeDefined();
    expect(screen.getByText("10 nguồn từ Wiki")).toBeDefined();
    const dropTable = screen.getByRole("table", { name: "Drop table" });
    expect(within(dropTable).getAllByRole("row")).toHaveLength(11);
    expect(
      within(dropTable).getByRole("columnheader", { name: "Nguồn" }).className,
    ).toContain("w-[58%]");
    expect(within(dropTable).getByRole("columnheader", { name: "Số lượng" })).toBeDefined();
    expect(within(dropTable).getByRole("columnheader", { name: "Tỷ lệ" })).toBeDefined();
    expect(within(dropTable).getByRole("columnheader", { name: "Điều kiện" })).toBeDefined();
    expect(screen.getByText("1-3")).toBeDefined();
    expect(screen.getByText("40%")).toBeDefined();
    expect(screen.getByText("Khi mất trí")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Usage" })).toBeDefined();
    expect(screen.getByText("1 công thức từ Wiki")).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Don't Starve" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Shipwrecked" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Hamlet" })).toBeNull();
    const baseUsageTable = screen.getByRole("table", {
      name: "Usage: Don't Starve",
    });
    expect(within(baseUsageTable).getAllByRole("row")).toHaveLength(2);
    expect(
      within(baseUsageTable).getByRole("columnheader", { name: "Công thức" }),
    ).toBeDefined();
    expect(
      within(baseUsageTable).getByRole("columnheader", {
        name: "Trạm / Nhân vật",
      }),
    ).toBeDefined();
    expect(
      within(baseUsageTable).getByRole("columnheader", { name: "Thành phẩm" }),
    ).toBeDefined();

    const recipeCells = within(baseUsageTable).getAllByRole("cell");
    expect(recipeCells).toHaveLength(3);
    expect(
      within(recipeCells[0]).getByLabelText("Nhiên liệu Ác Mộng, số lượng 2"),
    ).toBeDefined();
    expect(
      within(recipeCells[0]).getByRole("link", {
        name: "Gold Nugget, số lượng 8",
      }),
    ).toBeDefined();
    expect(
      within(recipeCells[1]).getByRole("link", {
        name: "Broken Pseudoscience Station",
      }),
    ).toBeDefined();
    expect(
      within(recipeCells[2]).getByRole("button", {
        name: "Đèn bóng đêm, số lượng 1",
      }),
    ).toBeDefined();
    const result = screen.getByRole("button", {
      name: "Đèn bóng đêm, số lượng 1",
    });
    const resultSprite = within(result).getByTestId("game-sprite");
    expect(resultSprite.className).toContain(
      "rounded-[4px]",
    );
    expect(resultSprite.style.width).toBe("48px");
    expect(resultSprite.style.height).toBe("48px");
    expect(result.getAttribute("aria-describedby")).toBe(
      screen.getByRole("tooltip", { name: "Đèn bóng đêm" }).id,
    );

    const fuel = screen.getAllByLabelText("Nhiên liệu Ác Mộng, số lượng 2")[0];
    expect(within(fuel).getByTestId("game-sprite")).toBeDefined();
    expect(within(fuel).getAllByText("Nhiên liệu Ác Mộng")).toHaveLength(1);
    expect(fuel.getAttribute("aria-describedby")).toBe(
      screen.getAllByRole("tooltip", { name: "Nhiên liệu Ác Mộng" })[0].id,
    );

    const gold = screen.getByRole("link", {
      name: "Gold Nugget, số lượng 8",
    });
    const goldIcon = within(gold).getByTestId("wiki-usage-icon");
    expect(goldIcon.className).toContain(
      "rounded-[4px]",
    );
    expect(goldIcon.getAttribute("width")).toBe("48");
    expect(goldIcon.getAttribute("height")).toBe("48");
    expect(goldIcon.className).toContain("size-[48px]");
    expect(within(gold).getByText("Gold Nugget").getAttribute("role")).toBe("tooltip");

    const brokenStation = screen.getByRole("link", {
      name: "Broken Pseudoscience Station",
    });
    expect(within(brokenStation).getByTestId("wiki-usage-icon")).toBeDefined();
    expect(
      decodeURIComponent(
        within(brokenStation).getByTestId("wiki-usage-icon").getAttribute("src") ?? "",
      ),
    ).toContain(
      "https://dontstarve.wiki.gg/images/thumb/Navbox_Broken_Pseudoscience_Station.png/50px-Navbox_Broken_Pseudoscience_Station.png?926476",
    );
    expect(
      within(brokenStation)
        .getByText("Broken Pseudoscience Station")
        .getAttribute("role"),
    ).toBe("tooltip");
    expect(brokenStation.getAttribute("aria-describedby")).toBe(
      screen.getByRole("tooltip", { name: "Broken Pseudoscience Station" }).id,
    );
    expect(screen.queryByRole("link", { name: "Prestihatitator" })).toBeNull();
    expect(screen.queryByText("Warly")).toBeNull();
    expect(screen.queryByText("Chỉ dùng trong DLC.")).toBeNull();
    expect(screen.queryByRole("link", { name: "Shadow Manipulator" })).toBeNull();
    expect(screen.queryByText("Chỉ dùng trong Hamlet.")).toBeNull();
    expect(screen.queryByRole("link", { name: "Seaworthy, số lượng 1" })).toBeNull();
    expect(screen.queryByRole("link", { name: "Skyworthy, số lượng 1" })).toBeNull();
    expect(
      screen.queryByText("Only available in the world linked with a Shipwrecked world."),
    ).toBeNull();
    expect(
      screen.queryByText("Only available in the world linked with a Hamlet world."),
    ).toBeNull();
    const beardlingLink = screen.getByRole("link", { name: "Beardling" });
    expect(beardlingLink.className).toContain("whitespace-nowrap");
    expect(beardlingLink.firstElementChild?.getAttribute("data-testid")).toBe(
      "wiki-source-icon",
    );
    expect(beardlingLink.firstElementChild?.className).toContain("rounded-[4px]");
    expect(beardlingLink.firstElementChild?.getAttribute("width")).toBe("48");
    expect(beardlingLink.firstElementChild?.getAttribute("height")).toBe("48");
    expect(beardlingLink.firstElementChild?.className).toContain("size-[48px]");
    expect(beardlingLink.firstElementChild?.tagName).toBe("IMG");
    expect(
      decodeURIComponent(beardlingLink.firstElementChild?.getAttribute("src") ?? ""),
    ).toContain(
      "https://dontstarve.wiki.gg/wiki/Special:Redirect/file/Beardling.png",
    );
    expect(beardlingLink).toHaveProperty(
      "href",
      "https://dontstarve.wiki.gg/wiki/Beardling",
    );
    expect(
      screen.getByRole("link", { name: "Gold Nugget, số lượng 8" }),
    ).toBeDefined();
  });

  it("opens a resolved catalog item inside the current detail flow", () => {
    const onSelectItem = vi.fn();
    render(
      <WikiStructuredSections
        sections={sections}
        itemsById={catalogItems}
        onSelectItem={onSelectItem}
      />,
    );

    fireEvent.click(
      screen.getByRole("button", { name: "Đèn bóng đêm, số lượng 1" }),
    );

    expect(onSelectItem).toHaveBeenCalledWith(nightLight);
  });
});
