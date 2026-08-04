import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { CharacterCatalogEntry } from "@/app/lib/character-catalog";
import { CharacterGallery } from "../character-gallery";

function makeCharacter(
  overrides: Partial<CharacterCatalogEntry> = {},
): CharacterCatalogEntry {
  return {
    id: "tu_tien:xd_wukong",
    code: "xd_wukong",
    namespace: "tu_tien",
    name: "Tôn Ngộ Không",
    englishName: "Sun Wukong",
    title: "Tề Thiên Đại Thánh",
    description: "Chiến binh biến hóa.",
    portrait: "/assets/dst/characters/xd_wukong.png",
    stats: {
      health: { value: 200, display: null, note: null },
      hunger: { value: 175, display: null, note: null },
      sanity: { value: 150, display: null, note: null },
    },
    abilities: [{ name: "Biến hóa", effect: "Đổi kỹ thuật." }],
    startingItems: [],
    artifacts: [
      {
        code: "ruyibang",
        name: "Như Ý Kim Cô Bổng",
        quantity: null,
        effect: "Mở biến hóa.",
        icon: null,
      },
    ],
    guide: {
      roles: ["Cận chiến"],
      attackPattern: "Áp sát mục tiêu.",
      range: "melee",
      complexity: "advanced",
      summary: "Hồ sơ chiến thuật.",
      strengths: ["Khống chế tốt."],
      tradeoffs: ["Cần pháp bảo."],
      firstSteps: ["Hạ yêu thú."],
      combat: [
        {
          label: "Căn Khí",
          description: "Mở hiệu ứng.",
          confidence: "confirmed",
        },
      ],
      realmMilestones: [
        {
          realm: "Trúc Cơ",
          unlocks: [
            {
              label: "Đồng Đầu Thiết Tý",
              description: "Mở tại Trúc Cơ.",
              confidence: "confirmed",
            },
          ],
        },
      ],
      artifacts: [],
    },
    ...overrides,
  };
}

const characters = [
  makeCharacter(),
  makeCharacter({
    id: "base_game:wanda",
    code: "wanda",
    namespace: "base_game",
    name: "Wanda",
    englishName: "Wanda",
    title: "Người giữ thời gian",
    portrait: "/assets/dst/characters/base/wanda.png",
    guide: null,
  }),
];

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("CharacterGallery", () => {
  it("searches Vietnamese and English names without accents", () => {
    render(<CharacterGallery characters={characters} />);
    const search = screen.getByRole("searchbox", { name: "Tìm nhân vật" });

    fireEvent.change(search, { target: { value: "ton" } });
    expect(screen.getByText("Tôn Ngộ Không")).toBeDefined();
    expect(screen.queryByText("Wanda")).toBeNull();

    fireEvent.change(search, { target: { value: "sun wukong" } });
    expect(screen.getByText("Tôn Ngộ Không")).toBeDefined();
  });

  it("filters Tu Tiên and base-game characters", () => {
    render(<CharacterGallery characters={characters} />);

    fireEvent.click(screen.getByRole("button", { name: "DST gốc" }));
    expect(screen.getByText("Wanda")).toBeDefined();
    expect(screen.queryByText("Tôn Ngộ Không")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Tu Tiên" }));
    expect(screen.getByText("Tôn Ngộ Không")).toBeDefined();
    expect(screen.queryByText("Wanda")).toBeNull();
  });

  it("opens every dossier section from the complete local DTO without fetching", async () => {
    const fetchMock = vi.fn(() => {
      throw new Error("Character dossiers must not use the network");
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<CharacterGallery characters={characters} />);

    fireEvent.click(
      screen.getByRole("button", { name: "Mở hồ sơ Tôn Ngộ Không" }),
    );
    const dialog = screen.getByRole("dialog", { name: "Tôn Ngộ Không" });
    expect(within(dialog).getByRole("heading", { name: "Tổng quan" })).toBeDefined();

    fireEvent.mouseDown(within(dialog).getByRole("tab", { name: "Chiến đấu" }), {
      button: 0,
      ctrlKey: false,
    });
    await waitFor(() => expect(within(dialog).getByText("Căn Khí")).toBeDefined());
    fireEvent.mouseDown(within(dialog).getByRole("tab", { name: "Cảnh giới" }), {
      button: 0,
      ctrlKey: false,
    });
    await waitFor(() => expect(within(dialog).getByText("Trúc Cơ")).toBeDefined());
    fireEvent.mouseDown(within(dialog).getByRole("tab", { name: "Pháp bảo" }), {
      button: 0,
      ctrlKey: false,
    });
    await waitFor(() =>
      expect(within(dialog).getByText("Như Ý Kim Cô Bổng")).toBeDefined(),
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
