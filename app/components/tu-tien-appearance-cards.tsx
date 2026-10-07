import type { SpriteDescriptor } from "@/app/lib/item-catalog";
import type { ModWikiEntry } from "./tu-tien-hub";
import { GameSprite } from "./game-sprite";

export function TuTienAppearanceCards({ rows, sprites }: { rows: readonly ModWikiEntry[]; sprites: Readonly<Record<string, SpriteDescriptor>> }) {
  return <section aria-label="Ngoại hình Nyx" className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
    {rows.map(row => <article key={row.id} aria-label={row.title} className="min-w-0 overflow-hidden rounded-2xl border border-nova-border bg-nova-surface-soft">
      <div className="flex min-h-56 items-center justify-center border-b border-nova-border bg-nova-surface p-4"><GameSprite sprite={sprites[row.id] ?? null} size={200} label={`Ảnh ${row.title}`} rounded={false} /></div>
      <div className="p-4"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-nova-muted">Ngoại hình</p><h3 className="break-words text-base font-semibold">{row.title}</h3>
        <details className="mt-3 text-xs text-nova-muted"><summary className="cursor-pointer">Nguồn đối chiếu</summary><p className="mt-2 break-all">{row.source}; Tu Tiên 18.1/anim/{row.id.replace("appearance:","")}.zip</p></details>
      </div>
    </article>)}
  </section>;
}
