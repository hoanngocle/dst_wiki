import type { SpriteDescriptor } from "@/app/lib/item-catalog";
import type { ModWikiEntry } from "./tu-tien-hub";
import { GameSprite } from "./game-sprite";

const fields = ["Nhóm thuộc tính", "Trang bị", "Giá trị", "Giới hạn"];
const cell = "border-b border-nova-border px-4 py-3 align-top";

export function TuTienGemTable({ rows, sprites }: { rows: readonly ModWikiEntry[]; sprites: Readonly<Record<string, SpriteDescriptor>> }) {
  return <div className="max-h-[70vh] overflow-auto rounded-2xl border border-nova-border">
    <table aria-label="Bảng Đá Quý" className="w-full min-w-[760px] text-left text-sm">
      <thead className="sticky top-0 z-10 bg-nova-surface"><tr><th scope="col" className={cell}>Đá Quý</th>{fields.map(field => <th key={field} scope="col" className={`${cell} whitespace-nowrap`}>{field}</th>)}<th scope="col" className={cell}>Nguồn</th></tr></thead>
      <tbody>{rows.map(row => <tr key={row.id} className="bg-nova-surface-soft hover:bg-nova-surface">
        <th scope="row" className={`${cell} min-w-52 font-medium`}><div className="flex items-center gap-3">{sprites[row.id] ? <GameSprite sprite={sprites[row.id]} size={36} label={`Ảnh ${row.title}`} /> : null}<span>{row.title}</span></div>{row.text.map((text,index) => <p key={index} className="mt-2 text-sm font-normal text-nova-muted">{text}</p>)}</th>
        {fields.map(field => <td key={field} className={`${cell} min-w-32 text-nova-muted`}>{row.facts.find(fact => fact.label === field)?.value ?? "—"}</td>)}
        <td className={cell}><details><summary className="cursor-pointer text-nova-muted">Đối chiếu</summary><p className="mt-2 max-w-64 break-all text-xs text-nova-muted">{row.source}</p></details></td>
      </tr>)}</tbody>
    </table>
  </div>;
}
