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
  contract: "catalog",
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

const carrot: ItemListEntry = {
  id: "base_game:carrot",
  prefabId: "carrot",
  namespace: "base_game",
  category: "item",
  name: "Carrot",
  englishName: "Carrot",
  description: null,
  craftingNote: null,
  sprite: null,
  recipe: null,
  wiki: null,
};

const animalEvidence = [{ source: "fandom", locator: "revision:200" }];
const noneSection = {
  status: "none",
  values: [],
  reason: "source_has_no_values",
  evidence: animalEvidence,
};
const unknownSection = {
  status: "unknown",
  values: [],
  reason: "not_verified",
  evidence: animalEvidence,
};

function animalDetails(
  primaryCode: string,
  variants: Array<{ code: string; label: string; order: number; sprite: null }>,
) {
  return {
    contract: "category",
    identity: {
      primaryCode,
      prefabCodes: variants.map((variant) => variant.code),
      sourcePageId: 200,
      sourceUrl: "https://dontstarve.fandom.com/wiki/Bunnyman",
      revisionId: 201,
    },
    classification: { type: "mob", tags: ["Animals"], game: "DST" },
    variants,
    stats: {
      status: "known",
      values: [{ key: "max_health", label: "Health", value: 200, unit: "hp", sourceVariant: primaryCode, evidence: animalEvidence }],
      reason: null,
      evidence: animalEvidence,
    },
    effects: {
      status: "known",
      values: [{ key: "sanity_aura", label: "Sanity Aura", value: "25/min", unit: null, sourceVariant: primaryCode, evidence: animalEvidence }],
      reason: null,
      evidence: animalEvidence,
    },
    combat: {
      status: "known",
      values: [{ key: "attack_damage", label: "Damage", value: 40, unit: null, sourceVariant: primaryCode, evidence: animalEvidence }],
      reason: null,
      evidence: animalEvidence,
    },
    movement: unknownSection,
    traits: {
      status: "known",
      values: [{ text: "Turns into a Beardlord below 40% Sanity.", sourceVariant: null }],
      reason: null,
      evidence: animalEvidence,
    },
    loot: {
      status: "known",
      values: [{ item: { id: carrot.id, name: carrot.name, sprite: null }, quantity: "×2", chance: null, conditions: null, method: "kill", sourceVariant: primaryCode, game: "DST" }],
      reason: null,
      evidence: animalEvidence,
    },
    spawnsFrom: noneSection,
    notes: noneSection,
  } as unknown as MobDetails;
}

const bunnyman: ItemListEntry = {
  ...champion,
  id: "base_game:bunnyman",
  prefabId: "bunnyman",
  category: "mob",
  name: "Bunnyman",
  englishName: "Bunnyman",
  mob: animalDetails("bunnyman", [
    { code: "bunnyman", label: "Bunnyman", order: 0, sprite: null },
  ]),
};

const koalefant: ItemListEntry = {
  ...bunnyman,
  id: "base_game:koalefant_summer",
  prefabId: "koalefant_summer",
  name: "Koalefant",
  englishName: "Koalefant",
  mob: animalDetails("koalefant_summer", [
    { code: "koalefant_summer", label: "Summer Koalefant", order: 0, sprite: null },
    { code: "koalefant_winter", label: "Winter Koalefant", order: 1, sprite: null },
  ]),
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

  it("renders ordered Animals sections and navigable loot", () => {
    const onSelectItem = vi.fn();
    render(
      <MobSections
        item={bunnyman}
        itemsById={new Map([[carrot.id, carrot]])}
        onSelectItem={onSelectItem}
        titleId="bunnyman"
      />,
    );

    expect(screen.getByRole("heading", { name: "Stats" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Effects" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Combat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Movement" })).toBeDefined();
    expect(screen.getByText(/Beardlord/)).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: "Carrot" }));
    expect(onSelectItem).toHaveBeenCalledWith(carrot);
  });

  it("renders one variant selector and concise unknown state", () => {
    render(
      <MobSections
        item={koalefant}
        itemsById={new Map()}
        onSelectItem={vi.fn()}
        titleId="koalefant"
      />,
    );

    expect(screen.getByRole("tab", { name: "Winter Koalefant" })).toBeDefined();
    expect(screen.getByText("Chưa xác minh")).toBeDefined();
  });
});
