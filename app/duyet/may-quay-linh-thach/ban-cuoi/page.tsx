import type { Metadata } from "next";
import Link from "next/link";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { StaticGameSprite } from "@/app/components/static-game-sprite";
import rewards from "./rewards.json";

export const metadata: Metadata = {
  title: "Bản chốt Máy Quay Linh Thạch | DST Wiki",
  robots: { index: false, follow: false },
};
const pct = (n: string) => `${n.replace(".", ",")}%`;

export default function FinalSlotRewardsPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
    <SiteHeader /><DstPageShell><div className="px-4 py-9 sm:px-6 lg:px-8">
      <div className="flex flex-wrap gap-5 text-sm text-nova-accent underline underline-offset-4">
        <Link href="/duyet/may-quay-linh-thach">Bản cũ · 104 gói</Link>
        <Link href="/duyet/may-quay-linh-thach/hien-tai">Tu Tiên hiện tại · 131 gói</Link>
      </div>
      <p className="mt-7 text-sm font-semibold text-nova-accent">BẢN CHỐT · CÔNG TRÌNH TU TIÊN {rewards.version}</p>
      <h1 className="mt-2 text-3xl font-semibold sm:text-4xl">Máy Quay Linh Thạch</h1>
      <p className="mt-3 max-w-3xl leading-7 text-nova-muted">133 gói hợp nhất, cập nhật ngày 09/10/2026. Nhóm Quái đã rút còn 15 gói. Trúng một gói sẽ nhận đủ các món trong hàng đó. Boss và quái xuất hiện quanh máy.</p>
      <section className="mt-6 rounded-2xl border border-nova-border bg-nova-surface p-5">
        <h2 className="text-xl font-semibold">Chi phí và tỷ lệ</h2>
        <p className="mt-3 leading-7 text-nova-muted">Mỗi lượt dùng 60 Hạ Phẩm Linh Thạch hoặc 1 Linh Thạch Trung / Thượng / Cực Phẩm. Các phẩm cấp dùng chung tỷ lệ.</p>
        <p className="mt-2 leading-7 text-nova-muted">Tỷ lệ dưới đây áp dụng khi đủ mod và có đất trống. Gói thiếu vật phẩm hoặc không có vị trí xuất hiện sẽ được loại khỏi lựa chọn; tỷ lệ những gói còn lại trong nhóm được tính lại. Máy từ chối trước khi thu tiền nếu không thể chọn gói hợp lệ.</p>
        <p className="mt-2 leading-7 text-nova-muted">Đã bỏ Nhất Vũ Phương Hoa và Thần Hi Quang Trượng vì thiếu bản tùy chỉnh cũ. Vẫn giữ hạt giống Phủ Băng ×3 và Đá Sa Mạc ×3 trong hai gói tương ứng.</p>
        <p className="mt-2 text-sm leading-6 text-nova-faint">Lượt bị gián đoạn khi tải lại hoặc lỗi trả thưởng được hoàn Linh Thạch cạnh máy. Các Boss cần biển hoặc sự kiện riêng đã được loại; giữ các biến thể Solo phù hợp trên đất.</p>
      </section>
      <nav aria-label="Nhóm phần thưởng" className="my-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {rewards.groups.map(g => <a key={g.id} href={`#${g.id}`} className="rounded-xl border border-nova-border bg-nova-surface p-4 hover:border-nova-accent"><span className="block font-semibold">{g.name} ↓</span><span className="mt-2 block text-xl text-nova-accent">{pct(g.chance)}</span><span className="text-xs text-nova-muted">{g.count} gói</span></a>)}
      </nav>
      <p className="mb-5 text-sm text-nova-muted">Tỷ lệ mỗi hàng là xác suất nhận trọn gói trong một lượt, bao gồm xác suất chọn nhóm.</p>
      <div className="space-y-7">{rewards.groups.map(g => <section key={g.id} id={g.id} className="scroll-mt-6 overflow-hidden rounded-2xl border border-nova-border bg-nova-surface">
        <h2 className="border-b border-nova-border p-5 text-xl font-semibold">{g.name} · {g.count} gói · {pct(g.chance)}</h2>
        <div className="overflow-x-auto" role="region" aria-label={`Bảng thưởng ${g.name}`} tabIndex={0}><table className="w-full min-w-[620px] text-left text-sm">
          <thead className="bg-nova-surface-soft text-nova-muted"><tr><th scope="col" className="px-5 py-3">Gói</th><th scope="col" className="px-3 py-3">Toàn bộ phần thưởng</th><th scope="col" className="px-5 py-3 text-right">Tỷ lệ / lượt</th></tr></thead>
          <tbody className="divide-y divide-nova-border">{g.bundles.map(b => <tr key={b.id} className="align-top">
            <th scope="row" className="px-5 py-5 font-semibold">{b.name}</th>
            <td className="px-3 py-4"><ul className="grid gap-3 xl:grid-cols-2">{b.items.map(i => <li key={i.prefab} className="flex items-center gap-3">
              <StaticGameSprite sprite={i.sprite} size={38} /><div><p>{i.name} <strong className="whitespace-nowrap text-nova-accent">×{i.amount}</strong></p><code className="break-all text-[11px] text-nova-faint">{i.prefab}</code>{"treasure" in i && <p className="text-xs text-nova-muted">Solo: {String(i.treasure)}</p>}</div>
            </li>)}</ul></td><td className="whitespace-nowrap px-5 py-5 text-right tabular-nums">{pct(b.chance)}</td>
          </tr>)}</tbody>
        </table></div>
      </section>)}</div>
      <a href="/duyet/may-quay-linh-thach/SLOT_REWARDS_FINAL.md" download className="mt-7 inline-block text-nova-accent underline underline-offset-4">Tải bảng chốt 133 gói (.md)</a>
    </div></DstPageShell>
  </div>;
}
