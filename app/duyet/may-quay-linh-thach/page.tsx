import type { Metadata } from "next";
import Link from "next/link";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import { StaticGameSprite } from "@/app/components/static-game-sprite";
import rewards from "./rewards.json";

export const metadata: Metadata = {
  title: "Duyệt bảng thưởng Máy Quay Linh Thạch | DST Wiki",
  description: "Trang tạm để duyệt 104 gói thưởng của Máy Quay Thưởng Linh Thạch trong bản Phàm Nhân Tu Tiên cũ.",
  robots: { index: false, follow: false },
};

const percent = (value: string) => `${value.replace(".", ",")}%`;
const sourcePath = "/duyet/may-quay-linh-thach";

export default function SlotRewardsReviewPage() {
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <Link href="/" className="text-sm font-medium text-nova-accent underline underline-offset-4">← Về wiki</Link>
          <p className="mt-4 rounded-xl border border-nova-border bg-nova-surface p-4 text-sm"><Link href="/duyet/may-quay-linh-thach/hien-tai" className="font-semibold text-nova-accent underline underline-offset-4">Xem bảng của Tu Tiên 18.1.0 đang cài: 131 gói →</Link></p>
          <header className="mt-6">
            <p className="inline-flex rounded-full border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-900">Trang tạm · Chờ duyệt</p>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">Máy Quay Thưởng Linh Thạch</h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-nova-muted">Bảng thưởng tìm lại từ bản Phàm Nhân Tu Tiên cũ: 104 gói, chia thành năm nhóm. Đây là bản tham khảo để duyệt, chưa áp dụng vào mod đang chơi.</p>
            <p className="mt-2 text-sm text-nova-faint">Máy trong bản này: <code>ttk_choujiangji</code> · Linh Thạch dùng mã <code>ttk_*</code>.</p>
          </header>

          <section aria-labelledby="cach-quay" className="mt-7 rounded-2xl border border-nova-border bg-nova-surface p-5 sm:p-7">
            <h2 id="cach-quay" className="text-xl font-semibold">1 Trung Phẩm Linh Thạch = 1 lượt</h2>
            <p className="mt-3 text-sm leading-7 text-nova-muted">Máy chọn nhóm trước, sau đó chọn một gói trong nhóm đó. Người chơi nhận <strong className="text-nova-text">toàn bộ nội dung gói</strong>. Nhóm Boss và Quái gọi sinh vật ra cạnh máy.</p>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-nova-muted">
              <li>Trang bị tối đa một chiếc mỗi loại trong một gói; các lượt vẫn có thể trùng quà.</li>
              <li>Đã bỏ sáo Pan; thay đồ sơ cấp bằng linh thảo, linh thực, nguyên liệu và pháp bảo Tu Tiên Ký.</li>
              <li>Không có cơ chế bảo hiểm. Tỷ lệ dưới đây áp dụng khi tất cả prefab được nạp; máy bỏ cả gói thiếu prefab trước khi chọn.</li>
            </ul>
            <p className="mt-4 border-t border-nova-border pt-4 text-sm leading-6 text-nova-muted"><strong className="text-nova-text">Công thức máy:</strong> 6 Đá Cắt + 4 Ván Gỗ + 2 Bánh Răng + 1 Ngọc Tím + 30 Hạ Phẩm Linh Thạch; học tại Máy Luyện Kim.</p>
          </section>

          <nav aria-label="Nhóm phần thưởng" className="my-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {rewards.groups.map(group => (
              <a key={group.id} href={`#${group.id}`} className="rounded-xl border border-nova-border bg-nova-surface p-4 transition-colors hover:border-nova-accent focus-visible:outline-2 focus-visible:outline-nova-accent">
                <span className="flex items-center justify-between gap-2 text-sm font-semibold">{group.name}<span aria-hidden="true">↓</span></span>
                <span className="mt-2 block text-xl font-semibold tabular-nums text-nova-accent">{percent(group.chance)}</span>
                <span className="mt-1 block text-xs text-nova-muted">{group.count} gói · xác suất mỗi lượt</span>
              </a>
            ))}
          </nav>

          <p className="mb-6 text-sm leading-6 text-nova-muted">Mỗi hàng là một kết quả quay. Cột tỷ lệ là xác suất nhận cả gói trong một lượt, đã tính cả xác suất nhóm. Mã vật phẩm được giữ dưới tên để đối chiếu chính xác.</p>

          <div className="space-y-7">
            {rewards.groups.map(group => (
              <section key={group.id} id={group.id} aria-labelledby={`${group.id}-title`} className="scroll-mt-6 overflow-hidden rounded-2xl border border-nova-border bg-nova-surface">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-nova-border p-5 sm:px-7">
                  <h2 id={`${group.id}-title`} className="text-xl font-semibold">{group.name} <span className="text-sm font-normal text-nova-muted">· {group.count} gói</span></h2>
                  <p className="text-sm font-semibold tabular-nums text-nova-accent">{percent(group.chance)} mỗi lượt</p>
                </div>
                <div className="overflow-x-auto" role="region" aria-label={`Bảng thưởng ${group.name}`} tabIndex={0}>
                  <table className="w-full min-w-[620px] text-left text-sm">
                    <caption className="sr-only">Danh sách gói thưởng {group.name}, vật phẩm, số lượng và xác suất mỗi lượt</caption>
                    <thead className="bg-nova-surface-soft text-xs text-nova-muted">
                      <tr><th scope="col" className="w-[22%] px-5 py-3 sm:pl-7">Gói thưởng</th><th scope="col" className="px-3 py-3">Nhận toàn bộ vật phẩm bên dưới</th><th scope="col" className="w-32 px-5 py-3 text-right sm:pr-7">Tỷ lệ / lượt</th></tr>
                    </thead>
                    <tbody className="divide-y divide-nova-border">
                      {group.bundles.map(bundle => (
                        <tr key={bundle.name} className="align-top">
                          <th scope="row" className="px-5 py-5 font-semibold sm:pl-7">{bundle.name}</th>
                          <td className="px-3 py-4">
                            <ul className="grid gap-3 xl:grid-cols-2">
                              {bundle.items.map(item => (
                                <li key={item.prefab} className="flex min-w-0 items-center gap-3">
                                  <StaticGameSprite sprite={item.sprite} size={38} />
                                  <div className="min-w-0">
                                    <p className="leading-5">{item.name} <strong className="whitespace-nowrap text-nova-accent">×{item.amount}</strong></p>
                                    {item.name !== item.prefab && <code className="mt-0.5 block break-all text-[11px] leading-4 text-nova-faint">{item.prefab}</code>}
                                  </div>
                                </li>
                              ))}
                            </ul>
                          </td>
                          <td className="whitespace-nowrap px-5 py-5 text-right font-medium tabular-nums sm:pr-7">{percent(bundle.chance)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            ))}
          </div>

          <section aria-labelledby="nguon" className="mt-7 rounded-2xl border border-nova-border bg-nova-surface p-5 sm:p-7">
            <h2 id="nguon" className="text-xl font-semibold">Đối chiếu với bản cũ</h2>
            <p className="mt-3 text-sm leading-7 text-nova-muted">Tài liệu kiểm kê ghi nhận 183 prefab của máy Tu Tiên gốc: <strong className="text-nova-text">126 giữ lại, 44 thay thế, 1 bỏ theo yêu cầu, 12 chưa chuyển</strong>. Giữ trọng số năm nhóm gốc; hai gói Cửu Thiên Tinh Thần Phiên và Tử Xá Diện Giáp có trọng số bằng một nửa các gói hiếm còn lại.</p>
            <p className="mt-3 text-sm leading-7 text-nova-muted">Bản thưởng được lưu ngày 21/09/2026 trong commit <code>8ee73588</code>. Trang này lấy bảng từ snapshot <code>7aa737ad</code>, ngay trước khi source mod được gỡ khỏi repo wiki ngày 23/09/2026. Tên và hình minh họa lấy từ danh mục wiki; mã, số lượng và tỷ lệ giữ theo tài liệu cũ.</p>
            <div className="mt-4 flex flex-wrap gap-x-6 gap-y-3 text-sm font-medium text-nova-accent">
              <a href={`${sourcePath}/CHOUJIANGJI_REWARDS.md`} download className="underline underline-offset-4">Tải bảng thưởng gốc (.md)</a>
              <a href={`${sourcePath}/CHOUJIANGJI_AUDIT.md`} download className="underline underline-offset-4">Tải danh sách giữ / thay / bỏ (.md)</a>
              <a href="#" className="underline underline-offset-4">Về đầu trang ↑</a>
            </div>
          </section>
        </div>
      </DstPageShell>
    </div>
  );
}
