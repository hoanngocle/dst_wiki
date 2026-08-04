import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { CharacterCatalogEntry } from "@/app/lib/character-catalog";
import { CharacterArtifacts } from "../character-artifacts";
import { CharacterCombat } from "../character-combat";
import { CharacterOverview } from "../character-overview";
import { CharacterRealms } from "../character-realms";

const sprite = {
  src: "/assets/game/tu-tien-artifact.png",
  uv: { u1: 0, u2: 1, v1: 0, v2: 1 },
};

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
    stats: {},
    abilities: [{ name: "Biến hóa", effect: "Đổi kỹ thuật." }],
    startingItems: [
      {
        code: "starter",
        name: "Khởi Nguyên Kiếm",
        quantity: 2,
        effect: "Trang bị khởi đầu.",
        icon: sprite,
      },
    ],
    artifacts: [
      {
        code: "artifact",
        name: "Như Ý Kim Cô Bổng",
        quantity: null,
        effect: "Mở biến hóa.",
        icon: sprite,
      },
    ],
    guide: {
      roles: ["Cận chiến"],
      attackPattern: "Áp sát mục tiêu.",
      range: "melee",
      complexity: "advanced",
      summary: "Hồ sơ đã xác minh.",
      strengths: ["Khống chế tốt."],
      tradeoffs: ["Cần pháp bảo."],
      firstSteps: ["Hạ yêu thú."],
      combat: [
        {
          label: "Kỹ thuật suy luận",
          description: "Diễn giải từ Mật Quyển.",
          confidence: "interpreted",
        },
        {
          label: "Mốc chưa xác định",
          description: "Chưa rõ thời điểm mở.",
          confidence: "unknown",
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
        {
          realm: "Kết Đan",
          unlocks: [
            {
              label: "An Thân Thuật",
              description: "Mở tại Kết Đan.",
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

describe("character dossier sections", () => {
  it("renders overview guidance and resolved starting-item sprites", () => {
    render(<CharacterOverview character={makeCharacter()} />);

    expect(screen.getByText("Hồ sơ đã xác minh.")).toBeDefined();
    expect(screen.getByText("Điểm mạnh")).toBeDefined();
    expect(screen.getByText("Khởi Nguyên Kiếm ×2")).toBeDefined();
    expect(screen.getByTestId("game-sprite").getAttribute("style")).toContain(
      "/assets/game/tu-tien-artifact.png",
    );
  });

  it("uses public confidence notes and preserves realm order", () => {
    const character = makeCharacter();
    const { rerender } = render(<CharacterCombat character={character} />);

    expect(screen.getByText("Theo Mật Quyển")).toBeDefined();
    expect(screen.getByText("Chưa rõ mốc chính xác")).toBeDefined();
    expect(screen.queryByText("interpreted")).toBeNull();
    expect(screen.queryByText("unknown")).toBeNull();

    rerender(<CharacterRealms character={character} />);
    const timeline = screen.getByTestId("realm-timeline");
    expect(
      within(timeline)
        .getAllByRole("heading", { level: 3 })
        .map((heading) => heading.textContent),
    ).toEqual(["Trúc Cơ", "Kết Đan"]);
  });

  it("renders artifact sprites without recipe metadata", () => {
    render(<CharacterArtifacts character={makeCharacter()} />);

    expect(screen.getByText("Như Ý Kim Cô Bổng")).toBeDefined();
    expect(screen.getByTestId("game-sprite").getAttribute("style")).toContain(
      "/assets/game/tu-tien-artifact.png",
    );
    expect(screen.queryByText(/công thức|recipe|nguyên liệu/i)).toBeNull();
  });

  it("shows a deliberate profile-only state when no guide exists", () => {
    render(
      <CharacterCombat
        character={makeCharacter({
          id: "base_game:wilson",
          code: "wilson",
          namespace: "base_game",
          name: "Wilson",
          englishName: "Wilson",
          title: "Nhà khoa học lịch lãm",
          description: "Wilson mọc một bộ râu tuyệt đẹp.",
          guide: null,
        })}
      />,
    );

    expect(screen.getByText("Hồ sơ cơ bản")).toBeDefined();
    expect(screen.getByText("Nhà khoa học lịch lãm")).toBeDefined();
    expect(screen.getByText(/chưa có hướng dẫn chiến thuật/i)).toBeDefined();
  });
});
