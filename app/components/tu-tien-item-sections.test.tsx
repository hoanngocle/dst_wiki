import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import { TuTienItemSections } from "./tu-tien-item-sections";


const resultItem: ItemListEntry = {
  id: "tu_tien:spirit_pill",
  prefabId: "spirit_pill",
  namespace: "tu_tien",
  category: "item",
  name: "Linh Đan",
  englishName: null,
  description: null,
  craftingNote: null,
  sprite: null,
  recipe: null,
  details: {
    recipeStatus: "unknown",
    usage: { status: "unknown", recipes: [], effects: [] },
    dropBy: { status: "unknown", sources: [] },
  },
  wiki: null,
};

const sourceItem: ItemListEntry = {
  ...resultItem,
  id: "tu_tien:spirit_plant",
  prefabId: "spirit_plant",
  name: "Cây Linh Thảo",
};

const petals: ItemListEntry = {
  ...resultItem,
  id: "base_game:petals",
  prefabId: "petals",
  namespace: "base_game",
  name: "Cánh hoa",
  details: null,
};

const herb: ItemListEntry = {
  ...resultItem,
  id: "tu_tien:herb",
  prefabId: "herb",
  name: "Linh Thảo",
  craftingNote: "Chế tạo tại lò luyện đan.",
  recipe: {
    outputCount: 2,
    ingredients: [
      {
        id: "base_game:petals",
        name: "Cánh hoa",
        amount: 3,
        sprite: null,
      },
    ],
  },
  details: {
    recipeStatus: "known",
    usage: {
      status: "known",
      recipes: [
        {
          result: { id: resultItem.id, name: resultItem.name, sprite: null },
          resultAmount: 1,
          subjectAmount: 2,
          ingredients: [
            {
              id: "base_game:goldnugget",
              name: "Vàng",
              amount: 1,
              sprite: null,
            },
          ],
          craftingNote: "Yêu cầu người chế tạo xd_alchemist.",
        },
      ],
      effects: [
        {
          trigger: "eat",
          text: "Khi ăn: hồi 20 Máu và hồi 10 Tinh thần.",
          evidence: [
            {
              source: "public/data/catalog.json",
              locator: "tu_tien:herb:stats",
            },
          ],
        },
      ],
    },
    dropBy: {
      status: "known",
      sources: [
        {
          type: "harvest",
          source: { id: sourceItem.id, name: sourceItem.name, sprite: null },
          quantity: "1–2",
          chance: "100%",
          conditions: "Hồi lại sau 480 giây",
          evidence: [
            {
              source: "public/data/catalog.json",
              locator: "tu_tien:herb:acquisition",
            },
          ],
        },
      ],
    },
  },
};

describe("TuTienItemSections", () => {
  it("renders Mob stats, special mechanics, and kill loot", () => {
    const mob: ItemListEntry = {
      ...resultItem,
      id: "tu_tien:xd_boss",
      prefabId: "xd_boss",
      category: "mob",
      name: "Yêu Vương",
      mob: {
        stats: [
          { key: "max_health", label: "Máu tối đa", value: 2500, unit: "hp" },
          { key: "attack_damage", label: "Sát thương", value: 80, unit: "hp" },
        ],
        mechanics: ["Trạng thái đặc biệt: charge, summon"],
        lootStatus: "known",
        loot: [
          {
            item: { id: petals.id, name: petals.name, sprite: null },
            quantity: "2",
            chance: "50%",
            conditions: null,
          },
        ],
      },
    };
    render(
      <TuTienItemSections
        item={mob}
        itemsById={new Map([[petals.id, petals]])}
        onSelectItem={vi.fn()}
        titleId="mob-title"
      />,
    );

    expect(screen.getByRole("heading", { name: "Chỉ số" })).toBeDefined();
    expect(screen.getByText("2.500")).toBeDefined();
    expect(screen.getByText("Trạng thái đặc biệt: charge, summon")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Vật phẩm rơi khi tiêu diệt" })).toBeDefined();
    expect(screen.getByText("50%")).toBeDefined();
  });

  it("renders the complete character profile instead of item recipe sections", () => {
    const character: ItemListEntry = {
      ...resultItem,
      id: "tu_tien:xd_hero",
      prefabId: "xd_hero",
      category: "character",
      name: "Anh Hùng",
      character: {
        title: "Kiếm Tu",
        survivability: "Gai Góc",
        quote: "Một kiếm phá trời.",
        abilities: ["Đi trên mây", "Dùng kiếm"],
      },
    };
    render(
      <TuTienItemSections
        item={character}
        itemsById={new Map()}
        onSelectItem={vi.fn()}
        titleId="character-title"
      />,
    );

    expect(screen.getByText("Kiếm Tu")).toBeDefined();
    expect(screen.getByText("Gai Góc")).toBeDefined();
    expect(screen.getByText("Một kiếm phá trời.")).toBeDefined();
    expect(screen.getByText("Đi trên mây")).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Công thức" })).toBeNull();
  });

  it("renders recipe, reverse usage, gameplay effects, and acquisition sources", () => {
    const onSelectItem = vi.fn();
    render(
      <TuTienItemSections
        item={herb}
        itemsById={new Map([
          [petals.id, petals],
          [resultItem.id, resultItem],
          [sourceItem.id, sourceItem],
        ])}
        onSelectItem={onSelectItem}
        titleId="herb-title"
      />,
    );

    const headings = screen.getAllByRole("heading").map((heading) => heading.textContent);
    expect(headings).toEqual(["Công thức", "Usage", "Nguồn nhận"]);
    expect(screen.getByLabelText("Cánh hoa, số lượng 3")).toBeDefined();
    expect(screen.getByLabelText("Kết quả: Linh Thảo, số lượng 2")).toBeDefined();
    expect(screen.getByText("Khi ăn: hồi 20 Máu và hồi 10 Tinh thần.")).toBeDefined();
    expect(screen.getByText("Dùng ×2 để chế tạo")).toBeDefined();
    expect(screen.getByText("Vàng ×1")).toBeDefined();
    expect(screen.getByText("1–2")).toBeDefined();
    expect(screen.getByText("100%")).toBeDefined();
    expect(screen.getByText("Hồi lại sau 480 giây")).toBeDefined();

    fireEvent.click(screen.getByRole("button", { name: "Cánh hoa, số lượng 3" }));
    fireEvent.click(screen.getByRole("button", { name: "Linh Đan" }));
    fireEvent.click(screen.getByRole("button", { name: "Cây Linh Thảo" }));
    expect(onSelectItem).toHaveBeenNthCalledWith(1, petals);
    expect(onSelectItem).toHaveBeenNthCalledWith(2, resultItem);
    expect(onSelectItem).toHaveBeenNthCalledWith(3, sourceItem);
  });

  it("keeps all sections visible for none and unknown states", () => {
    render(
      <TuTienItemSections
        item={{
          ...herb,
          recipe: null,
          craftingNote: null,
          details: {
            recipeStatus: "none",
            usage: { status: "unknown", recipes: [], effects: [] },
            dropBy: { status: "none", sources: [] },
          },
        }}
        itemsById={new Map()}
        onSelectItem={vi.fn()}
        titleId="unknown-title"
      />,
    );

    expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Usage" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Nguồn nhận" })).toBeDefined();
    expect(screen.getByText("Không có công thức chế tạo.")).toBeDefined();
    expect(screen.getByText("Chưa xác định từ dữ liệu mod.")).toBeDefined();
    expect(screen.getByText("Không có nguồn nhận ngoài chế tạo.")).toBeDefined();
  });
});
