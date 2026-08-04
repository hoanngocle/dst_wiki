import type { SpriteDescriptor } from "@/app/lib/item-catalog";
import { spriteCropStyle } from "@/app/lib/sprite";

export function StaticGameSprite({
  sprite,
  size,
}: {
  sprite: SpriteDescriptor | null;
  size: number;
}) {
  if (!sprite) {
    return (
      <span
        aria-hidden="true"
        data-missing="true"
        data-testid="static-game-sprite"
        className="inline-flex shrink-0 items-center justify-center rounded-xl border border-nova-border bg-nova-surface-soft text-xs text-nova-faint"
        style={{ width: size, height: size }}
      >
        ?
      </span>
    );
  }

  return (
    <span
      aria-hidden="true"
      data-testid="static-game-sprite"
      className="inline-block shrink-0 overflow-hidden rounded-xl bg-nova-surface-soft"
      style={spriteCropStyle(sprite, size)}
    />
  );
}
