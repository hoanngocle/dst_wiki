import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { CharacterCatalogEntry } from "@/app/lib/character-catalog";
import { CharacterCard } from "../character-card";

const character: CharacterCatalogEntry = {
  id: "tu_tien:xd_wukong",
  code: "xd_wukong",
  namespace: "tu_tien",
  name: "Tôn Ngộ Không",
  englishName: "Sun Wukong",
  title: "Tề Thiên Đại Thánh",
  description: "Chiến binh biến hóa với Như Ý Kim Cô Bổng.",
  portrait: "/assets/dst/characters/xd_wukong.png",
  stats: {
    health: { value: 200, display: null, note: null },
    hunger: { value: 175, display: null, note: null },
    sanity: { value: 150, display: null, note: null },
  },
  abilities: [{ name: "Đồng Đầu Thiết Tý", effect: "Áp sát mục tiêu." }],
  startingItems: [],
  artifacts: [],
  guide: {
    roles: ["Cận chiến", "Biến hóa"],
    attackPattern: "Đồng Đầu Thiết Tý áp sát mục tiêu.",
    range: "melee",
    complexity: "advanced",
    summary: "Một hồ sơ đã được xác minh.",
    strengths: ["Khống chế tốt."],
    tradeoffs: ["Cần pháp bảo."],
    firstSteps: ["Hạ yêu thú."],
    combat: [],
    realmMilestones: [{ realm: "Trúc Cơ", unlocks: [] }],
    artifacts: [],
  },
};

describe("CharacterCard", () => {
  it("presents the curated dossier without item-catalog metadata", () => {
    const { container } = render(
      <CharacterCard character={character} onOpen={() => undefined} />,
    );

    expect(screen.getByText("Tu Tiên")).toBeDefined();
    expect(screen.getByText("Tôn Ngộ Không")).toBeDefined();
    expect(screen.getByText("Tề Thiên Đại Thánh")).toBeDefined();
    expect(screen.getByText("Cận chiến, Biến hóa")).toBeDefined();
    expect(screen.getByText("Chuyên sâu")).toBeDefined();
    expect(screen.getByText("Trúc Cơ")).toBeDefined();
    expect(screen.queryByText(/công thức|recipe|nguyên liệu/i)).toBeNull();
    expect(container.querySelectorAll("[data-character-chip]")).toHaveLength(3);
  });

  it("uses one full-card button and a decorative resolved portrait", () => {
    const onOpen = vi.fn();
    const { container } = render(
      <CharacterCard character={character} onOpen={onOpen} />,
    );

    const button = screen.getByRole("button", {
      name: "Mở hồ sơ Tôn Ngộ Không",
    });
    expect(screen.getAllByRole("button")).toHaveLength(1);
    expect(container.querySelector("img")?.getAttribute("src")).toBe(
      "/assets/dst/characters/xd_wukong.png",
    );
    expect(container.querySelector("img")?.getAttribute("alt")).toBe("");

    fireEvent.click(button);
    expect(onOpen).toHaveBeenCalledOnce();
    expect(onOpen).toHaveBeenCalledWith(character);
  });
});
