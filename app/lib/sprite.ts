import type { CSSProperties } from "react";

import type { SpriteDescriptor } from "./item-catalog";

export function spriteCropStyle(sprite: SpriteDescriptor, size: number): CSSProperties {
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
