import { ImageBroken } from "@phosphor-icons/react";
import type { CSSProperties } from "react";

import type { SpriteDescriptor } from "@/app/lib/item-catalog";

type GameSpriteProps = {
  sprite: SpriteDescriptor | null;
  size: number;
  className?: string;
  label?: string;
  rounded?: boolean;
};

function cropStyle(sprite: SpriteDescriptor, size: number): CSSProperties {
  const { u1, u2, v1, v2 } = sprite.uv;
  const width = u2 - u1;
  const height = v2 - v1;
  const x = width >= 1 ? 50 : (u1 / (1 - width)) * 100;
  const yTop = 1 - v2;
  const y = height >= 1 ? 50 : (yTop / (1 - height)) * 100;

  return {
    width: size,
    height: size,
    backgroundImage: `url("${sprite.src}")`,
    backgroundPosition: `${x}% ${y}%`,
    backgroundRepeat: "no-repeat",
    backgroundSize: `${100 / width}% ${100 / height}%`,
  };
}

export function GameSprite({
  sprite,
  size,
  className = "",
  label,
  rounded = true,
}: GameSpriteProps) {
  const semantics = label
    ? { role: "img", "aria-label": label }
    : { "aria-hidden": true as const };
  const cornerClass = rounded ? "rounded-xl" : "";

  if (!sprite) {
    return (
      <span
        {...semantics}
        data-missing="true"
        data-testid="game-sprite"
        className={`inline-flex shrink-0 items-center justify-center overflow-hidden border border-[#c8d3df] bg-[#e5ebf1] text-[#607188] ${cornerClass} ${className}`}
        style={{ width: size, height: size }}
      >
        <ImageBroken aria-hidden="true" size={Math.max(16, Math.round(size * 0.42))} />
      </span>
    );
  }

  return (
    <span
      {...semantics}
      data-testid="game-sprite"
      className={`inline-block shrink-0 overflow-hidden bg-[#e5ebf1] ${cornerClass} ${className}`}
      style={cropStyle(sprite, size)}
    />
  );
}
