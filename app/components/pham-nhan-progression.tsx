"use client";

import { useState } from "react";
import data from "@/data/generated/pham-nhan-progression.json";
import { DstPanel } from "./dst-panel";

const seasons: Record<string, string> = { spring: "Xuân", summer: "Hạ", autumn: "Thu", winter: "Đông" };
const cell = "border-t border-nova-border px-4 py-3 text-left align-top";
const heading = "text-2xl font-semibold tracking-[-0.03em]";
const groups: Record<string, string> = {
  survival: "Sinh tồn", food: "Ẩm thực", combat: "Chiến đấu", collection: "Sưu tầm",
  crafting: "Chế tạo", farming: "Canh tác", boss: "Boss", dungeon_guild: "Bí cảnh và hội",
  enhancement: "Cường hóa", gacha_shop: "Quay thưởng và cửa hàng", labor: "Lao động",
  level_rank: "Cấp và hạng", seasonal: "Theo mùa",
};
const bundle = (items: { prefab: string; amount: number }[]) => items.map((item) => `${item.prefab} × ${item.amount}`).join(" · ");

type Pill = (typeof data.cultivation)[number] & { effect?: { kind: string; duration?: number } };

function PillTable({ label, rows, cultivation = false }: { label: string; rows: readonly Pill[]; cultivation?: boolean }) {
  return <div className="mt-4 overflow-x-auto"><table aria-label={label} className="w-full min-w-[40rem] text-sm">
    <thead><tr><th className={cell}>Đan dược</th><th className={cell}>Nguyên liệu</th><th className={cell}>Công dụng</th></tr></thead>
    <tbody>{rows.map((row, index) => <tr key={row.prefab}>
      <th scope="row" className={cell}>{row.name}<code className="mt-1 block text-xs font-normal text-nova-muted">{row.prefab}</code></th>
      <td className={cell}>{bundle(row.recipe.ingredients)}</td>
      <td className={cell}>{cultivation ? `Tu luyện bậc ${index + 1}; dùng theo thứ tự từ bậc ${index}.` : row.effect?.kind === "cold_protection" ? `Chống lạnh trong ${row.effect.duration} giây.` : row.effect?.kind === "heat_protection" ? `Chống nóng trong ${row.effect.duration} giây.` : row.effects.map((effect) => effect.text).join(" ")}</td>
    </tr>)}</tbody>
  </table></div>;
}

export function PhamNhanProgression() {
  const [query, setQuery] = useState("");
  const [group, setGroup] = useState("");
  const search = query.trim().toLocaleLowerCase("vi");
  const achievements = data.achievements.filter((row) => (!group || row.group === group) && `${row.id} ${row.name} ${row.description}`.toLocaleLowerCase("vi").includes(search));
  return <div className="space-y-8">
    <DstPanel className="p-5 sm:p-6">
      <h2 className={heading}>Một cấp nhân vật, một tiến trình tu luyện</h2>
      <p className="mt-3 leading-7 text-nova-muted">Cấp nhân vật dùng chung hệ thống hh_leveling đã tích hợp, bao gồm kỹ năng EVA. Tu luyện bằng đan là tiến trình riêng gồm 15 bậc, không phải thanh Level thứ hai. Star nhận từ thành tựu dùng để mua kỹ năng; nhiệm vụ mùa nhận vật phẩm theo mốc.</p>
      <div className="mt-4 overflow-x-auto"><table aria-label="Hạng nhân vật" className="w-full text-sm"><thead><tr><th className={cell}>Hạng</th><th className={cell}>Cấp yêu cầu</th></tr></thead><tbody>{data.ranks.map((rank) => <tr key={rank.name}><th className={cell}>{rank.name}</th><td className={cell}>{rank.level}</td></tr>)}</tbody></table></div>
    </DstPanel>
    <DstPanel className="p-5 sm:p-6">
      <h2 className={heading}>Thành tựu và Star</h2>
      <div className="my-4 flex flex-wrap gap-3">
        <input type="search" aria-label="Tìm thành tựu" placeholder="Tên hoặc mã thành tựu…" value={query} onChange={(event) => setQuery(event.target.value)} className="min-h-11 min-w-0 flex-1 rounded-lg border border-nova-border bg-nova-surface px-4" />
        <select aria-label="Nhóm thành tựu" value={group} onChange={(event) => setGroup(event.target.value)} className="min-h-11 rounded-lg border border-nova-border bg-nova-surface px-4"><option value="">Tất cả {data.groups.length} nhóm</option>{data.groups.map((id) => <option key={id} value={id}>{groups[id] ?? id}</option>)}</select>
      </div>
      <p role="status" className="text-sm text-nova-muted">{achievements.length} / {data.achievements.length} thành tựu</p>
      <div className="mt-3 max-h-[36rem] overflow-auto"><table aria-label="Thành tựu" className="w-full min-w-[36rem] text-sm"><thead><tr><th className={cell}>Thành tựu</th><th className={cell}>Điều kiện</th><th className={cell}>Mục tiêu</th><th className={cell}>Star</th></tr></thead><tbody>{achievements.map((row) => <tr key={row.id}><th scope="row" className={cell}>{row.name}<code className="mt-1 block text-xs font-normal text-nova-muted">{row.id}</code></th><td className={cell}>{row.description}</td><td className={cell}>{row.target}</td><td className={cell}>{row.reward}</td></tr>)}</tbody></table></div>
      {achievements.length === 0 && <p className="mt-4 text-nova-muted">Không tìm thấy thành tựu phù hợp.</p>}
    </DstPanel>
    <DstPanel className="p-5 sm:p-6">
      <h2 className={heading}>Kỹ năng mua bằng Star</h2>
      <p className="mt-3 text-nova-muted">Giá kỹ năng nhiều bậc: bậc 1–10 giá 2, 11–15 giá 3, 16–20 giá 4, 21–25 giá 5 Star mỗi bậc.</p>
      <div className="mt-4 overflow-x-auto"><table aria-label="Kỹ năng Star" className="w-full min-w-[32rem] text-sm"><thead><tr><th className={cell}>Kỹ năng</th><th className={cell}>Nhóm</th><th className={cell}>Số bậc</th><th className={cell}>Tổng Star</th></tr></thead><tbody>{data.perks.map((row) => <tr key={row.id}><th scope="row" className={cell}>{row.name}<code className="mt-1 block text-xs font-normal text-nova-muted">{row.id}</code></th><td className={cell}>{row.group}</td><td className={cell}>{row.levelPrices.length || 1}</td><td className={cell}>{row.maxCost}</td></tr>)}</tbody></table></div>
    </DstPanel>
    <DstPanel className="p-5 sm:p-6">
      <h2 className={heading}>Nhiệm vụ mùa</h2>
      <p className="mt-3 leading-7 text-nova-muted">Mỗi mùa có 50 nhiệm vụ trong kho: 40 một lần và 10 lặp lại. Mỗi lượt mùa rút 20 nhiệm vụ; nhiệm vụ lặp lại nhận tối đa 5 lần. Chỉ lần nhận đầu tiên của mỗi nhiệm vụ tính vào các mốc rương 5 / 10 / 15 / 20; phần thưởng không cấp Star.</p>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">{data.seasons.map((season) => <section key={season.id} className="min-w-0 rounded-xl border border-nova-border p-4"><h3 className="text-xl font-semibold">Mùa {seasons[season.id]} · {season.tasks.length} nhiệm vụ</h3><p className="mt-2 text-sm text-nova-muted">{season.draw.once + season.draw.repeat} nhiệm vụ mỗi mùa: {season.draw.once} một lần + {season.draw.repeat} lặp lại</p><ul className="mt-4 space-y-3 text-sm">{season.milestones.map((milestone) => <li key={milestone.completed}><strong>Mốc {milestone.completed}: </strong><span className="break-words">{bundle(milestone.items)}</span></li>)}</ul><details className="mt-4"><summary className="cursor-pointer font-semibold">Xem kho nhiệm vụ mùa {seasons[season.id]}</summary><ul className="mt-3 max-h-80 space-y-3 overflow-auto text-sm">{season.tasks.map((task) => <li key={task.id}><strong>{task.name}</strong> — {task.description} <span className="text-nova-muted">(Mục tiêu {task.target}; tối đa {task.max_claims} lần)</span><code className="block text-xs text-nova-muted">{task.id}</code></li>)}</ul></details></section>)}</div>
    </DstPanel>
    <DstPanel className="p-5 sm:p-6">
      <h2 className={heading}>15 đan tu luyện</h2>
      <p className="mt-3 leading-7 text-nova-muted">Đan Lô luyện trong {data.furnace.duration} giây với đúng nguyên liệu của công thức. Dùng đan lần lượt để mở từng bậc tu luyện; tiến trình này độc lập với cấp nhân vật.</p>
      <PillTable label="Đan tu luyện" rows={data.cultivation} cultivation />
    </DstPanel>
    <DstPanel className="p-5 sm:p-6">
      <h2 className={heading}>10 đan buff</h2>
      <PillTable label="Đan buff" rows={data.buffs} />
      <h3 className="mt-6 text-lg font-semibold">{data.fasting.name}</h3><p className="mt-2 text-sm leading-6 text-nova-muted">Tốc độ hao Đói còn {data.fasting.effect.multiplier * 100}% bình thường.</p>
    </DstPanel>
  </div>;
}
