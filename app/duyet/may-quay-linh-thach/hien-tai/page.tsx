import type { Metadata } from "next";
import Link from "next/link";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { StaticGameSprite } from "@/app/components/static-game-sprite";
import rewards from "./rewards.json";

export const metadata: Metadata = {
  title: "Bảng thưởng hiện tại — Tu Tiên 18.1.0 | DST Wiki",
  robots: { index: false, follow: false },
};

const percent = (value: string) => `${value.replace(".", ",")}%`;

export default function CurrentSlotRewardsPage() {
  return <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
    <SiteHeader />
    <DstPageShell>
      <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
        <Link href="/duyet/may-quay-linh-thach" className="text-sm text-nova-accent underline underline-offset-4">← Đối chiếu bản chỉnh cũ: 104 gói</Link>
        <p className="mt-6 text-sm font-semibold text-nova-accent">BẢNG HIỆN TẠI · TU TIÊN {rewards.version}</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">Phần thưởng Máy Quay Linh Thạch</h1>
        <p className="mt-3 max-w-3xl text-base leading-7 text-nova-muted">131 gói lấy từ source Tu Tiên đang cài trên máy, đọc ngày 08/10/2026. Máy chọn nhóm, rồi chọn một gói; phát toàn bộ số lượng của mọi vật phẩm trong gói đó.</p>
        <p className="mt-2 text-sm text-nova-faint">Workshop {rewards.workshop} · Prefab <code>xd_choujiangji</code> · Trang tạm để đối chiếu</p>

        <section aria-label="Cách quay hiện tại" className="mt-6 rounded-2xl border border-nova-border bg-nova-surface p-5 sm:p-7">
          <h2 className="text-xl font-semibold">Cơ chế trong source đang cài</h2>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-7 text-nova-muted">
            <li>Nhận chồng <strong className="text-nova-text">60 Hạ Phẩm Linh Thạch</strong>, hoặc Linh Thạch Trung / Thượng / Cực Phẩm khi máy rảnh.</li>
            <li>Các phẩm cấp dùng chung bảng tỷ lệ. Đưa phẩm cao không tăng xác suất trúng đồ hiếm trong logic này.</li>
            <li>Vẫn có <strong className="text-nova-text">sáo Pan, đan dược và pháp bảo Tu Tiên</strong>. Boss và quái được gọi ra cạnh máy.</li>
            <li>Nhánh bảo đảm pháp bảo ở lượt đầu đang bị comment trong source.</li>
          </ul>
          <p className="mt-4 border-t border-nova-border pt-4 text-sm leading-6 text-nova-muted">Tỷ lệ được tính từ trọng số trong source và làm tròn bốn chữ số thập phân. Đây là xác nhận bằng đọc mã nguồn; chưa kiểm chứng lượt quay thực tế trong game.</p>
        </section>

        <nav aria-label="Nhóm phần thưởng" className="my-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {rewards.groups.map(group => <a key={group.id} href={`#${group.id}`} className="rounded-xl border border-nova-border bg-nova-surface p-4 hover:border-nova-accent">
            <span className="block text-sm font-semibold">{group.name} ↓</span>
            <span className="mt-2 block text-xl font-semibold tabular-nums text-nova-accent">{percent(group.chance)}</span>
            <span className="mt-1 block text-xs text-nova-muted">{group.count} gói</span>
          </a>)}
        </nav>

        <p className="mb-6 text-sm leading-6 text-nova-muted">Tỷ lệ mỗi hàng là xác suất nhận trọn gói trong một lượt, đã tính cả xác suất nhóm. Số gói theo thứ tự trong source; mã prefab giữ nguyên để đối chiếu.</p>
        <div className="space-y-7">
          {rewards.groups.map(group => <section key={group.id} id={group.id} aria-labelledby={`${group.id}-title`} className="scroll-mt-6 overflow-hidden rounded-2xl border border-nova-border bg-nova-surface">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-nova-border p-5">
              <h2 id={`${group.id}-title`} className="text-xl font-semibold">{group.name} · {group.count} gói</h2>
              <span className="text-sm font-semibold text-nova-accent">{percent(group.chance)} mỗi lượt</span>
            </div>
            <div className="overflow-x-auto" role="region" aria-label={`Bảng thưởng ${group.name}`} tabIndex={0}>
              <table className="w-full min-w-[620px] text-left text-sm">
                <caption className="sr-only">Phần thưởng hiện tại nhóm {group.name}</caption>
                <thead className="bg-nova-surface-soft text-xs text-nova-muted"><tr><th scope="col" className="w-24 px-5 py-3">Gói</th><th scope="col" className="px-3 py-3">Toàn bộ phần thưởng</th><th scope="col" className="w-32 px-5 py-3 text-right">Tỷ lệ / lượt</th></tr></thead>
                <tbody className="divide-y divide-nova-border">
                  {group.bundles.map(bundle => <tr key={bundle.name} className="align-top">
                    <th scope="row" className="px-5 py-5 font-semibold">{bundle.name}</th>
                    <td className="px-3 py-4"><ul className="grid gap-3 xl:grid-cols-2">
                      {bundle.items.map(item => <li key={item.prefab} className="flex min-w-0 items-center gap-3">
                        <StaticGameSprite sprite={item.sprite} size={38} />
                        <div className="min-w-0"><p className="leading-5">{item.name} <strong className="whitespace-nowrap text-nova-accent">×{item.amount}</strong></p>{item.name !== item.prefab && <code className="mt-0.5 block break-all text-[11px] text-nova-faint">{item.prefab}</code>}</div>
                      </li>)}
                    </ul></td>
                    <td className="whitespace-nowrap px-5 py-5 text-right font-medium tabular-nums">{percent(bundle.chance)}</td>
                  </tr>)}
                </tbody>
              </table>
            </div>
          </section>)}
        </div>

        <details className="mt-7 rounded-2xl border border-nova-border bg-nova-surface p-5 text-sm">
          <summary className="cursor-pointer font-semibold">Nguồn dữ liệu và bản tải xuống</summary>
          <p className="mt-3 leading-7 text-nova-muted">Đọc trực tiếp <code>scripts/prefabs/xd_choujiangji.lua</code> trong Workshop {rewards.workshop}, bản {rewards.version}. Nhóm hiếm có 14 gói trọng số 1 và hai gói pháp bảo trọng số 0,5; các gói trong mỗi nhóm còn lại có trọng số bằng nhau.</p>
          <p className="mt-2 break-all text-xs text-nova-faint">SHA-256 source: {rewards.sha256}</p>
          <a href="/duyet/may-quay-linh-thach/TU_TIEN_18_1_REWARDS.md" download className="mt-4 inline-block font-medium text-nova-accent underline underline-offset-4">Tải bảng đầy đủ 131 gói (.md)</a>
        </details>
      </div>
    </DstPageShell>
  </div>;
}
