import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { SpriteDescriptor } from "@/app/lib/item-catalog";
import { GameSprite } from "./game-sprite";

const fullSprite: SpriteDescriptor = {
  src: "/assets/game/full.png",
  uv: { u1: 0, u2: 1, v1: 0, v2: 1 },
};

describe("GameSprite", () => {
  it("renders a full texture without division-by-zero positions", () => {
    render(<GameSprite sprite={fullSprite} size={64} label="Kiếm Thử" />);

    const image = screen.getByRole("img", { name: "Kiếm Thử" });
    expect(image.style.backgroundSize).toBe("100% 100%");
    expect(image.style.backgroundPosition).toBe("50% 50%");
    expect(image.style.width).toBe("64px");
    expect(image.style.height).toBe("64px");
  });

  it("converts bottom-left UV coordinates into finite CSS crop values", () => {
    const sprite: SpriteDescriptor = {
      src: "/assets/game/atlas.png",
      uv: { u1: 0.25, u2: 0.5, v1: 0.5, v2: 0.75 },
    };
    render(<GameSprite sprite={sprite} size={32} label="Vàng" />);

    const image = screen.getByRole("img", { name: "Vàng" });
    expect(image.style.backgroundSize).toBe("400% 400%");
    expect(image.style.backgroundPosition).toBe(
      "33.33333333333333% 33.33333333333333%",
    );
    expect(image.style.backgroundImage).toContain("/assets/game/atlas.png");
  });

  it("marks an unlabeled sprite as decorative", () => {
    render(<GameSprite sprite={fullSprite} size={40} />);

    expect(screen.getByTestId("game-sprite").getAttribute("aria-hidden")).toBe("true");
  });

  it("renders a stable fallback when the sprite is missing", () => {
    render(<GameSprite sprite={null} size={48} label="Thiếu ảnh" />);

    expect(
      screen.getByRole("img", { name: "Thiếu ảnh" }).getAttribute("data-missing"),
    ).toBe("true");
  });
});
