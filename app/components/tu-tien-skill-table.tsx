import type { SpriteDescriptor } from "@/app/lib/item-catalog";
import type { ModWikiEntry } from "./tu-tien-hub";
import { GameSprite } from "./game-sprite";

const cell = "border-b border-nova-border px-4 py-3 align-top";
const details: Record<string, { damage: string[]; effect: string; source: string }> = {
  absolute_domain: { damage: ["67 × M₃₀ + W"], effect: "Lĩnh vực quanh Nyx, bán kính 6; gây sát thương mỗi 0,5 giây. Hiệu ứng gốc tồn tại 15 giây.", source: "scripts/components/nyx_domain.lua; Tu Tiên 18.1/scripts/prefabs/xd_luoshen_shentong_fx.lua" },
  triflame_fan: { damage: ["Lửa quạt: (50 × M₂₅ + W) × 2", "Lửa phụ truy đuổi: (110 × M₂₅ + W) × 2"], effect: "Phóng 5 luồng lửa theo hình quạt trong khoảng 8 giây, kèm 5 ngọn lửa phụ truy đuổi. Các luồng dùng chung danh sách trúng đòn; không cộng đơn giản thành 5 lần sát thương.", source: "scripts/nyx/attack18.lua; scripts/nyx/fan_shadowfire.lua; Tu Tiên 18.1/scripts/prefabs/xd_htz_firefx.lua và xd_mutated_fx.lua" },
  yellow_river: { damage: ["240 × M₃₀ + W"], effect: "Tạo trận quanh Nyx, gây sát thương và làm chậm; sinh đá và hồi 1,5% máu tối đa cho mục tiêu hợp lệ của vùng hồi. Vùng trận tồn tại 31 giây.", source: "scripts/nyx/yellow_river.lua; Tu Tiên 18.1/scripts/prefabs/xd_yunxiao_jjj.lua" },
  eternal_night: { damage: ["Tia vùng: (100 × M₂₅ + W) × 2 mỗi giây", "Lửa truy đuổi: (220 × M₂₅ + W) × 2 mỗi lần trúng"], effect: "Chọn kẻ địch gần điểm thi triển, trói mục tiêu bằng tia vùng bán kính 6 và tạo các đợt lửa truy đuổi.", source: "scripts/nyx/attack18.lua; scripts/prefabs/nyx_wmz_spell.lua" },
  spirit_sword: { damage: ["Đạn kiếm: (60 × M₁₅ + W) × 3", "Tia kiếm: (300 × M₁₅ + W) × 3 mỗi 0,5 giây", "Trận kiếm: (1101 × M₁₅ + W) × 3"], effect: "Triệu hồi 5 kiếm quanh điểm chọn và trận kiếm ở giữa. Đạn kiếm nổ bán kính 3; tia và trận kiếm đánh trong bán kính 6. Hủy hiệu ứng còn lại sau 12 giây.", source: "scripts/nyx/attack18.lua; scripts/prefabs/nyx_htz_xtzlj.lua" },
  purple_gather: { damage: ["Không gây sát thương"], effect: "Tự động thu gom quanh điểm chọn. Bán kính tăng theo cấp, tối đa 12; bậc thu gom tối đa 10. Phí giảm từ 20 xuống 6 Linh Lực ở cấp 80.", source: "scripts/components/nyx_gather.lua; scripts/nyx/progression.lua" },
  purple_eye: { damage: ["Không gây sát thương"], effect: "Bật/tắt nhìn đêm và thêm modifier tinh thần +0,5. Tiêu hao 4 Linh Lực/giây; giảm còn 3 ở cấp 50, 2 ở cấp 70, 1 ở cấp 100.", source: "scripts/nyx/utility18.lua; scripts/nyx/progression.lua" },
  moon_wings: { damage: ["Không gây sát thương"], effect: "Bật/tắt cánh, đi trên nước và tăng tốc 8%. Tiêu hao 4 Linh Lực/giây; giảm còn 3 ở cấp 70, 2 ở cấp 90, 1 ở cấp 100. Cần xuống thú cưỡi để dùng.", source: "scripts/nyx/utility18.lua; scripts/nyx/progression.lua" },
  bean_soldiers: { damage: ["Đòn phân thân: 20 × L + W", "Nổ triệu hồi: 200 + 100 × ⌊L/10⌋ + W"], effect: "Ném đạn triệu hồi 3 phân thân. Sát thương phân thân tăng 20 mỗi cấp, không giới hạn theo mốc 100; AI và thời gian tồn tại do Tu Tiên quản lý.", source: "scripts/nyx/attack18.lua; scripts/util/nyx_skill_damage.lua" },
};

export function TuTienSkillTable({ rows, sprites }: { rows: readonly ModWikiEntry[]; sprites: Readonly<Record<string, SpriteDescriptor>> }) {
  const fact = (row: ModWikiEntry, label: string) => row.facts.find(value => value.label === label)?.value ?? "—";
  return <section className="mb-6" aria-label="Tra cứu kỹ năng Nyx">
    <h3 className="mb-3 text-lg font-semibold">Kỹ năng Nyx</h3>
    <div className="max-h-[70vh] overflow-auto rounded-2xl border border-nova-border"><table aria-label="Kỹ năng Nyx" className="w-full min-w-[1250px] text-left text-sm"><thead className="sticky top-0 z-10 bg-nova-surface"><tr>{["Kỹ năng", "Phím", "Mở khóa", "Linh Lực cơ bản", "Hồi chiêu", "Sát thương mỗi lần trúng", "Hiệu ứng", "Nguồn"].map(label => <th scope="col" key={label} className={cell}>{label}</th>)}</tr></thead><tbody>{rows.map(row => {
      const info = details[row.id];
      return <tr key={row.id} className="bg-nova-surface-soft hover:bg-nova-surface"><th scope="row" className={`${cell} min-w-52 font-medium`}><div className="flex items-center gap-3">{sprites[row.id] ? <GameSprite sprite={sprites[row.id]} size={40} label={`Ảnh ${row.title}`} /> : null}{row.title}</div></th>
        {["Phím", "Mở khóa", "Linh lực cơ bản", "Hồi chiêu"].map(label => <td key={label} className={cell}>{fact(row,label)}</td>)}
        <td className={`${cell} min-w-72`}>{(info?.damage ?? ["Chưa đối chiếu sát thương"]).map(value => <p key={value} className="mb-2 font-medium last:mb-0">{value}</p>)}</td>
        <td className={`${cell} min-w-80 leading-6 text-nova-muted`}>{info?.effect}</td>
        <td className={cell}><details><summary className="cursor-pointer text-nova-muted">Đối chiếu</summary><p className="mt-2 min-w-48 break-words text-xs">{row.source}; Nyx_Steam_2026-09-27/{info?.source}; scripts/util/nyx_skill_damage.lua</p></details></td>
      </tr>;
    })}</tbody></table></div>
    <div className="mt-3 space-y-2 text-sm leading-6 text-nova-muted">
      <p><strong>L</strong> là cấp Nyx. <strong>W</strong> là sát thương vũ khí đang cầm, có tính thay đổi từ cường hóa/đá quý theo component vũ khí.</p>
      <p><strong>M₃₀ = 1 + 0,30 × n</strong>; <strong>M₂₅ = 1 + 0,25 × n</strong>; <strong>M₁₅ = 1 + 0,15 × n</strong>. Với cấp dưới 100: n = min(8, ⌊L/10⌋); từ cấp 100: n = 10. Vì vậy cấp 90 vẫn dùng n = 8.</p>
      <p>Số trên là sát thương đầu vào của bộ tính Tu Tiên cho từng lần trúng. Sát thương thực tế còn phụ thuộc buff, bonus, giáp và mục tiêu; chưa phải tổng sát thương của cả lần thi triển.</p>
      <p>Phí kỹ năng thường: max(phí cơ bản ÷ 2, phí cơ bản − 10 × ⌊L/10⌋). Tụ Linh dùng mức giảm riêng; Thần Nhãn và Nguyệt Dực tiêu hao theo giây khi bật.</p>
    </div>
  </section>;
}
