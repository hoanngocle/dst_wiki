import { GameSprite } from "@/app/components/game-sprite";
import type { SoloLevelingEntry, SoloLevelingShopProduct } from "@/app/lib/solo-leveling";

export function SoloLevelingShopCard({ entry, product }: { entry: SoloLevelingEntry; product: SoloLevelingShopProduct }) {
  return (
    <article id={entry.id} aria-labelledby={`${entry.id}-title`} className="catalog-card flex min-w-0 flex-col rounded-2xl border border-nova-border bg-nova-surface-soft p-4 shadow-[0_10px_28px_rgba(40,66,98,0.06)]">
      <div className="grid grid-cols-[72px_minmax(0,1fr)] items-center gap-3.5">
        <div>
          <GameSprite sprite={product.sprite} size={72} label={`Icon ${entry.title}`} className="ring-1 ring-nova-border" />
          {!product.sprite && <p className="mt-1 text-center text-[10px] text-nova-faint">Chưa có ảnh</p>}
        </div>
        <div className="min-w-0">
          <span className="inline-flex rounded-full border border-nova-accent/30 bg-nova-accent/10 px-2 py-0.5 text-[11px] font-semibold text-nova-accent">{product.rank ? `Rank ${product.rank}` : entry.category}</span>
          <h3 id={`${entry.id}-title`} className="mt-2 text-[17px] leading-6 font-semibold text-nova-text [overflow-wrap:anywhere]">{entry.title}</h3>
          <code className="mt-1 block truncate text-[11px] text-nova-faint" title={product.prefab}>{product.prefab}</code>
        </div>
      </div>
      {!product.rank && <p className="mt-4 text-sm leading-6 text-nova-muted">{entry.lines[0]}</p>}
      <p className="mt-5 text-xs text-nova-muted">Giá mỗi lượt</p>
      <p className="mt-1 text-lg font-semibold text-nova-accent">{product.price.toLocaleString("vi-VN")} {product.currency ?? "Xu Hiệp Hội"}</p>
      <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-nova-border pt-4 text-sm">
        <div><dt className="text-xs text-nova-muted">Nhận mỗi lượt</dt><dd className="mt-1 font-semibold">{product.amount} vật phẩm</dd></div>
        <div><dt className="text-xs text-nova-muted">{product.rank ? "Giới hạn mua" : "Số lượt bán"}</dt><dd className="mt-1 font-semibold">{product.stock} lượt{product.rank ? " / chu kỳ" : ""}</dd></div>
      </dl>
      <details className="mt-4 border-t border-nova-border pt-3 text-xs leading-6 text-nova-faint">
        <summary className="cursor-pointer rounded-md font-medium focus-visible:outline-2 focus-visible:outline-nova-accent">Thông tin gốc</summary>
        <div className="mt-2 break-all">{entry.lines.map((line, index) => <p key={index}>{line}</p>)}<p className="mt-2">Nguồn: {entry.source}</p></div>
      </details>
    </article>
  );
}
