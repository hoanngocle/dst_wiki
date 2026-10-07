"use client";

import { useState, type ReactNode } from "react";
import type { ItemListEntry, SpriteDescriptor } from "@/app/lib/item-catalog";
import type { ModWiki, ModWikiEntry } from "./tu-tien-hub";
import { GameSprite } from "./game-sprite";

const cell = "border-b border-nova-border px-4 py-3 align-top";
const normalize = (value: string) => value.normalize("NFD").replace(/\p{M}/gu, "").replace(/đ/gi, "d").toLocaleLowerCase("vi");

function Table({ title, columns, children }: { title: string; columns: string[]; children: ReactNode }) {
  return <section className="mt-6"><h3 className="mb-3 text-lg font-semibold">{title}</h3><div className="max-h-[70vh] overflow-auto rounded-2xl border border-nova-border"><table aria-label={title} className="w-full min-w-[640px] text-left text-sm"><thead className="sticky top-0 z-10 bg-nova-surface"><tr>{columns.map(column => <th scope="col" key={column} className={cell}>{column}</th>)}</tr></thead><tbody className="bg-nova-surface-soft">{children}</tbody></table></div></section>;
}

const objects = [
  { id: "hn_dungeon_gate", title: "Cổng Hầm Ngục", use: "Dùng cổng để vào lượt chơi. Cổng có biểu tượng trên bản đồ; màu thay đổi theo độ khó và trạng thái hồi." },
  { id: "hn_dungeon_exit", title: "Lối thoát Hầm Ngục", use: "Dùng lối ra để trở về. Lối ra bị khóa trong lúc đánh boss; không dịch chuyển xuyên tường hoặc ranh giới." },
  { id: "hn_treasure_rock", title: "Mạch Linh Thạch", use: "Xuất hiện sau khi vượt ải: tối đa 6 mạch ở lượt 2–5 đợt, 12 mạch ở lượt 6–10 đợt. Đào 6 lần để nhận thưởng theo bảng bên dưới." },
  { id: "hn_recovery_bag", title: "Túi thu hồi Hầm Ngục", use: "Đồ rơi khi chết trong Hầm Ngục được đưa về túi tại vị trí cổng của lượt chơi. Túi sử dụng hình rương gỗ." },
];

export function TuTienDungeon({ mod, referenceItems, names, sprites }: { mod: ModWiki; referenceItems: readonly ItemListEntry[]; names: ReadonlyMap<string, string>; sprites: Readonly<Record<string, SpriteDescriptor>> }) {
  const [query, setQuery] = useState("");
  const terms = normalize(query).trim().split(/\s+/).filter(Boolean);
  const matches = (text: string) => terms.every(term => normalize(text).includes(term));
  const byPrefab = new Map(referenceItems.map(item => [item.prefabId, item]));
  const name = (prefab: string) => byPrefab.get(prefab)?.name ?? names.get(prefab) ?? prefab;
  const icon = (prefab: string) => sprites[prefab] ?? byPrefab.get(prefab)?.sprite;
  const matching = (row: ModWikiEntry) => matches([row.id, row.title, ...row.text, ...row.facts.map(f => `${f.label} ${f.value}`), ...row.ingredients.map(i => `${i.prefab} ${name(i.prefab)}`)].join(" "));
  const bosses = mod.entries.filter(row => row.category === "Boss" && matching(row));
  const rewards = mod.entries.filter(row => row.category === "Phần thưởng" && matching(row));
  const mobs = mod.entries.filter(row => row.category === "Vật phẩm" && /HN_DUNGEON_(SPIDER|PIG|.*HOUND)$/.test(row.id) && matching(row));
  const selectedObjects = objects.filter(row => matches(`${row.id} ${row.title} ${row.use}`));
  function image(prefab: string, title: string) {
    const sprite = icon(prefab);
    return sprite ? <GameSprite sprite={sprite} size={40} label={`Ảnh ${title}`} /> : null;
  }
  const fact = (row: ModWikiEntry, label: string) => row.facts.find(f => f.label === label)?.value ?? "—";
  return <section className="mt-8" aria-label={mod.name}>
    <div className="flex flex-wrap items-baseline gap-3"><h2 className="text-2xl font-semibold">Hầm Ngục</h2><span className="rounded-full bg-nova-surface-soft px-3 py-1 font-mono text-sm text-nova-muted">v{mod.version}</span></div>
    <Table title="Lượt chơi Hầm Ngục" columns={["Số đợt", "Boss đợt cuối", "Máu và sát thương quái", "Máu và sát thương boss"]}>
      <tr><th scope="row" className={cell}>2–5 đợt</th><td className={cell}>Deerclops, Bearger, Dragonfly, Ancient Guardian, Spider Queen, Treeguard hoặc Varg</td><td className={cell}>×2</td><td className={cell}>×1</td></tr>
      <tr><th scope="row" className={cell}>6–10 đợt</th><td className={cell}>Một trong 6 boss ở bảng bên dưới</td><td className={cell}>×3</td><td className={cell}>×1,5</td></tr>
    </Table>
    <Table title="Hướng dẫn Hầm Ngục" columns={["Tình huống", "Cách chơi / thời gian"]}>
      <tr><th scope="row" className={cell}>Chuẩn bị</th><td className={cell}>Bật Tu Tiên và Hầm Ngục cho mọi người chơi. Arena được tạo tại Forest khi tạo thế giới mới.</td></tr>
      <tr><th scope="row" className={cell}>Vượt ải</th><td className={cell}>Hạ hết quái để sang đợt tiếp theo; đợt cuối là boss. Đợt đầu bắt đầu sau 5 giây, các đợt sau cách nhau 10 giây.</td></tr>
      <tr><th scope="row" className={cell}>Nhặt thưởng</th><td className={cell}>Có 180 giây (3 phút) sau khi hạ boss để mở rương và đào mạch khoáng, rồi dùng lối ra.</td></tr>
      <tr><th scope="row" className={cell}>Hồi lượt</th><td className={cell}>Cổng và người chơi hồi 480 giây (8 phút). Chết trong Hầm Ngục áp dụng hồi 960 giây (16 phút).</td></tr>
    </Table>
    <input type="search" aria-label="Tìm trong Hầm Ngục" placeholder="Tìm boss, đồ dùng, vật phẩm thưởng…" value={query} onChange={event => setQuery(event.target.value)} className="mt-6 min-h-11 w-full rounded-xl border border-nova-border bg-nova-surface px-4" />
    <Table title="Phần thưởng Hầm Ngục" columns={["Lượt chơi", "Nguồn thưởng", "Tỷ lệ", "Vật phẩm nhận được"]}>
      {rewards.map(row => {
        const [,tier,kind] = row.id.split(":");
        return <tr key={row.id}><th scope="row" className={cell}>{tier === "1" ? "2–5 đợt" : "6–10 đợt"}</th><td className={cell}>{{ monster: "Mỗi quái", boss: "Rương sau boss", rock: "Mỗi mạch khoáng" }[kind]}</td><td className={cell}>{kind === "monster" ? "50%" : "100%"}</td><td className={cell}><div className="flex flex-col gap-2">{row.ingredients.map(ingredient => <div key={ingredient.prefab} className="flex items-center gap-3">{image(ingredient.prefab,name(ingredient.prefab))}<span>{name(ingredient.prefab)} <strong>×{ingredient.amount}</strong></span></div>)}</div></td></tr>;
      })}
    </Table>
    <p className="mt-3 text-sm leading-6 text-nova-muted">Rương còn chứa đồ rơi gốc của boss. Nếu không có prefab Huyền Tinh, 2 Huyền Tinh Hạ Phẩm được thay bằng 10 Linh Thạch Hạ Phẩm; 2 Huyền Tinh Trung Phẩm được thay bằng 20 Linh Thạch Hạ Phẩm.</p>
    <Table title="Đồ dùng Hầm Ngục" columns={["Đồ dùng", "Cách sử dụng"]}>{selectedObjects.map(row => <tr key={row.id}><th scope="row" className={cell}><div className="flex items-center gap-3">{image(row.id,row.title)}{row.title}</div></th><td className={cell}>{row.use}</td></tr>)}</Table>
    <Table title="Boss Hầm Ngục" columns={["Boss", "Máu cơ bản", "Sát thương cơ bản", "Sát thương phẳng"]}>{bosses.map(row => <tr key={row.id}><th scope="row" className={cell}>{row.title}</th>{["Máu cơ bản","Sát thương cơ bản","Sát thương phẳng"].map(label => <td key={label} className={cell}>{fact(row,label)}</td>)}</tr>)}</Table>
    <p className="mt-3 text-sm leading-6 text-nova-muted">Chỉ số trên là nền trước hệ số lượt chơi và bonus của mod khác. Lượt 6–10 đợt nhân máu và sát thương thường của boss ×1,5; phần nhân hệ số của Hầm Ngục không sửa sát thương phẳng. Dấu — là thông số chưa có trong dữ liệu đối chiếu.</p>
    <Table title="Quái Hầm Ngục" columns={["Quái riêng", "Nhóm đợt"]}>{mobs.map(row => <tr key={row.id}><th scope="row" className={cell}><div className="flex items-center gap-3">{image(row.id.replace("item:","").toLowerCase(),row.title)}{row.title}</div></th><td className={cell}>{row.id.endsWith("PIG") ? "Đợt heo ở lượt 6–10 đợt" : row.id.endsWith("SPIDER") ? "Đợt nhện" : "Đợt hỗn hợp 5 loại sói, mỗi loại 2 con"}</td></tr>)}</Table>
    <p className="mt-3 text-sm leading-6 text-nova-muted">Các đợt thường còn có nhện hang, Tallbird và Dê Điện. Lượt 6–10 đợt thêm quân cờ, Walrus và Warglet; mỗi đợt quái có 10 con.</p>
    {query && bosses.length + rewards.length + mobs.length + selectedObjects.length === 0 ? <p role="status" className="mt-4 text-nova-muted">Không tìm thấy nội dung phù hợp.</p> : null}
    <details className="mt-6 text-xs text-nova-muted"><summary className="cursor-pointer">Nguồn đối chiếu</summary><p className="mt-2 break-all">HamNgucTuTien/scripts/hn_dungeon: waves.lua, combat.lua, reward_defs.lua, rewards.lua, recovery.lua; scripts/components/hn_dungeon_manager.lua; scripts/prefabs; images/minimap và images/inventoryimages.</p></details>
  </section>;
}
