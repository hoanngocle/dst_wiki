import type { ItemListEntry } from "@/app/lib/item-catalog";
import { GameSprite } from "./game-sprite";
import { TuTienItemSections } from "./tu-tien-item-sections";

export function TuTienKySections({ item, itemsById, onSelectItem, titleId }: {
  item: ItemListEntry;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
  titleId: string;
}) {
  return <>
    {item.products?.length ? (
      <section aria-labelledby={`${titleId}-products`} className="overflow-hidden rounded-2xl border border-nova-border bg-nova-surface-soft">
        <h3 id={`${titleId}-products`} className="border-b border-nova-border px-4 py-3 text-sm font-semibold">Sản vật & thực thể liên quan</h3>
        <ul className="space-y-2 p-4">
          {item.products.map((product) => {
            const target = itemsById.get(product.item.id);
            return <li key={`${product.item.id}:${product.conditions}`} className="rounded-xl border border-nova-border bg-nova-surface-raised p-3 text-sm">
              <button type="button" disabled={!target} onClick={() => target && onSelectItem(target)}
                className="inline-flex min-h-11 items-center gap-2 rounded-lg font-semibold text-nova-accent hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent disabled:text-nova-text">
                <GameSprite sprite={product.item.sprite} size={32} />
                {product.item.name}
              </button>
              <p className="mt-1 font-medium">{product.quantity}</p>
              <p className="mt-1 leading-6 text-nova-muted">{product.conditions}</p>
            </li>;
          })}
        </ul>
      </section>
    ) : null}
    <TuTienItemSections item={item} itemsById={itemsById} onSelectItem={onSelectItem} titleId={titleId} />
  </>;
}
