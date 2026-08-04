import { ImageBroken } from "@phosphor-icons/react";

import type { SpriteDescriptor } from "@/app/lib/item-catalog";
import { spriteCropStyle } from "@/app/lib/sprite";

type GameSpriteProps = {
  sprite: SpriteDescriptor | null;
  size: number;
  className?: string;
  label?: string;
  rounded?: boolean;
};

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
        className={`inline-flex shrink-0 items-center justify-center overflow-hidden border border-nova-border bg-nova-surface-soft text-nova-muted ${cornerClass} ${className}`}
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
      className={`inline-block shrink-0 overflow-hidden bg-nova-surface-soft ${cornerClass} ${className}`}
      style={spriteCropStyle(sprite, size)}
    />
  );
}
