import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ItemListEntry, MobDetails } from "@/app/lib/item-catalog";
import { MobSections } from "./mob-sections";

const evidence = [{ source: "fixture", locator: "celestial-champion" }];
const crown: ItemListEntry = {
  id: "base_game:alterguardianhat",
  prefabId: "alterguardianhat",
  namespace: "base_game",
  category: "item",
  name: "Vương Miện Khai Sáng",
  englishName: "Enlightened Crown",
  description: null,
  craftingNote: null,
  sprite: null,
  recipe: null,
  wiki: null,
};
const details: MobDetails = {
  appearance: {
    status: "known",
    sources: ["Được triệu hồi tại Mysterious Energy"],
    spawnCodes: ["alterguardian_phase3", "alterguardian_phase3dead"],
    renewable: null,
    respawn: null,
    wikiUrl: "https://dontstarve.wiki.gg/wiki/Celestial_Champion",
    evidence,
  },
  variants: [
    {
      id: "base_game:alterguardian_phase3",
      prefabId: "alterguardian_phase3",
      name: "Celestial Champion",
      role: "phase",
      order: 3,
      sprite: null,
    },
    {
      id: "base_game:alterguardian_phase3dead",
      prefabId: "alterguardian_phase3dead",
      name: "Defeated Celestial Champion",
      role: "post_defeat",
      order: 4,
      sprite: null,
    },
  ],
  stats: [
    {
      key: "max_health",
      label: "Máu tối đa",
      value: 14000,
      unit: "hp",
      sourceVariant: "base_game:alterguardian_phase3",
      evidence,
    },
  ],
  mechanics: [
    {
      text: "Trạng thái đặc biệt: summon, spin",
      sourceVariant: "base_game:alterguardian_phase3",
      evidence,
    },
  ],
  lootStatus: "known",
  loot: [
    {
      item: { id: crown.id, name: crown.name, sprite: null },
      minimum: 1,
      maximum: 1,
      chance: "100%",
      method: "mine_post_defeat",
      sourceVariant: "base_game:alterguardian_phase3dead",
      lootTable: "alterguardian_phase3dead",
      conditions: "Bảng rơi: alterguardian_phase3dead",
      evidence,
    },
  ],
};
const champion: ItemListEntry = {
  id: "base_game:alterguardian_phase3",
  prefabId: "alterguardian_phase3",
  namespace: "base_game",
  category: "boss",
  name: "Nhà Vô Địch Thiên Giới",
  englishName: "Celestial Champion",
  description: null,
  craftingNote: null,
  sprite: null,
  recipe: null,
  mob: details,
  wiki: null,
};

describe("MobSections", () => {
  it("renders appearance, phases, mechanics, and clickable rewards", () => {
    const onSelectItem = vi.fn();
    render(
      <MobSections
        item={champion}
        itemsById={new Map([[crown.id, crown]])}
        onSelectItem={onSelectItem}
        titleId="champion"
      />,
    );

    expect(screen.getByRole("heading", { name: "Xuất hiện" })).toBeDefined();
    expect(screen.getByText("Giai đoạn hậu chiến")).toBeDefined();
    expect(screen.getByText("Khai thác xác bằng cuốc")).toBeDefined();
    expect(screen.getByText("14.000")).toBeDefined();

    fireEvent.click(screen.getByRole("button", { name: crown.name }));
    expect(onSelectItem).toHaveBeenCalledWith(crown);
  });
});
