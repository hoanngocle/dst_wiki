import { BookOpen, ClipboardText, Diamond, GearSix, Hammer, Medal, Package, UsersThree } from "@phosphor-icons/react";
import { GameSprite } from "@/app/components/game-sprite";
import type { SoloLevelingEntry } from "@/app/lib/solo-leveling";

const topicIcons = { guide: BookOpen, wiki: BookOpen, crafting: Hammer, daily: ClipboardText, items: Package, effects: Diamond, guild: ClipboardText, exams: Medal, shadows: UsersThree, config: GearSix };

function EntryLines({ lines }: { lines: string[] }) {
  return <div className="space-y-2 text-sm leading-6 text-nova-muted">{lines.map((line, index) => <p key={index} className="whitespace-pre-line [overflow-wrap:anywhere]">{line}</p>)}</div>;
}

export function SoloLevelingContentCard({ entry, topic }: { entry: SoloLevelingEntry; topic: string }) {
  const Icon = topicIcons[topic as keyof typeof topicIcons] ?? BookOpen;
  const document = topic === "guide" || topic === "wiki" || entry.tables.length > 0;
  const recipe = entry.recipe;
  const facts = entry.lines.filter((line) => /^(Mục tiêu:|Độ khó:|Rank:|Xu Hiệp Hội:|Thời hạn \(ngày\):|Vai trò:|Hoạt động nhận EXP:|\d+ EXP$)/.test(line));
  const details = entry.lines.filter((line) => !facts.includes(line));
  const remaining = recipe ? entry.lines : details.slice(details[0]?.startsWith("Kỹ năng theo cấp:") ? 0 : 1).filter((line) => !entry.talents || !line.startsWith("Kỹ năng theo cấp:"));
  return (
    <article id={entry.id} aria-labelledby={`${entry.id}-title`} className={`catalog-card flex min-w-0 scroll-mt-6 flex-col rounded-2xl border border-nova-border bg-nova-surface-soft p-4 sm:p-5 ${document ? "col-span-full" : ""}`}>
      <div className="flex items-center gap-3.5">
        {entry.sprite ? <GameSprite sprite={entry.sprite} size={64} label={`Icon ${entry.title}`} className="ring-1 ring-nova-border" /> : <span aria-hidden="true" className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl border border-nova-border bg-nova-accent/5 text-nova-accent"><Icon size={30} weight="duotone" /></span>}
        <div className="min-w-0">
          <p className="text-xs font-medium text-nova-accent">{entry.category}</p>
          <h3 id={`${entry.id}-title`} className="mt-1 text-lg leading-6 font-semibold tracking-[-0.02em] [overflow-wrap:anywhere]">{entry.title}</h3>
        </div>
      </div>
      {recipe ? <>
        <div className="mt-5 rounded-xl border border-nova-accent/20 bg-nova-accent/5 p-3">
          <p className="text-xs text-nova-muted">Sản phẩm nhận được</p>
          <p className="mt-1 font-semibold text-nova-accent">{recipe.amount} × {entry.title.replace(/^Dung hợp /, "")}</p>
        </div>
        <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-nova-faint">Nguyên liệu</p>
        <ul className="mt-2 space-y-2" aria-label={`Nguyên liệu ${entry.title}`}>
          {recipe.ingredients.map((ingredient, index) => <li key={index} className="flex items-center gap-3 rounded-xl border border-nova-border bg-nova-surface/60 p-2">
            <GameSprite sprite={ingredient.sprite ?? null} size={40} label={`Nguyên liệu ${ingredient.name}`} />
            <div className="min-w-0 text-sm"><p className="font-medium [overflow-wrap:anywhere]">{ingredient.amount} × {ingredient.name}</p><code className="break-all text-[10px] text-nova-faint">{ingredient.prefab}</code></div>
          </li>)}
        </ul>
        <p className="mt-4 flex items-start gap-2 text-sm leading-6 text-nova-muted"><Hammer className="mt-1 shrink-0" size={18} aria-hidden="true" /><span>Chế tạo tại: {recipe.station}</span></p>
      </> : <>
        {document ? <div className="mt-4"><EntryLines lines={entry.lines} /></div> : <>
          {details[0] && !details[0].startsWith("Kỹ năng theo cấp:") && <div className="mt-4"><EntryLines lines={[details[0]]} /></div>}
          {facts.length > 0 && <ul className="mt-4 grid gap-2 rounded-xl border border-nova-border bg-nova-surface/60 p-3 text-sm" aria-label="Thông tin chính">{facts.map((fact) => <li key={fact} className="font-medium [overflow-wrap:anywhere]">{fact}</li>)}</ul>}
          {entry.related && <div className="mt-4"><p className="mb-2 text-xs text-nova-faint">Một số mục tiêu hợp lệ</p><div className="flex flex-wrap gap-2">{entry.related.map((target) => <GameSprite key={target.prefab} sprite={target.sprite} size={40} label={`Mục tiêu ${target.name}`} />)}</div></div>}
        </>}
      </>}
      {entry.talents && <ol className="mt-4 space-y-2" aria-label={`Kỹ năng ${entry.title}`}>
        {entry.talents.map((talent) => <li key={talent.id} className="rounded-xl border border-nova-border bg-nova-surface/60 p-3"><div className="flex flex-wrap items-center gap-2"><span className="rounded-md bg-nova-accent/10 px-2 py-1 text-[11px] font-semibold text-nova-accent">Cấp {talent.level}</span><h4 className="text-sm font-semibold">{talent.name}</h4></div><p className="mt-2 whitespace-pre-line text-sm leading-6 text-nova-muted">{talent.desc}</p></li>)}
      </ol>}
      {entry.tables.map((table, index) => <div key={index} tabIndex={0} className="mt-4 overflow-x-auto rounded-lg border border-nova-border focus-visible:outline-2 focus-visible:outline-nova-accent">
        <table aria-label={`${entry.title} — bảng ${index + 1}`} className="w-full min-w-[36rem] border-collapse text-left text-sm"><thead className="bg-nova-surface-raised"><tr>{table.headers.map((header, column) => <th key={column} scope="col" className="px-4 py-3 font-semibold">{header}</th>)}</tr></thead><tbody>{table.rows.map((row, r) => <tr key={r} className="border-t border-nova-border">{row.map((cell, c) => c === 0 ? <th key={c} scope="row" className="px-4 py-3 font-medium">{cell}</th> : <td key={c} className="px-4 py-3 text-nova-muted">{cell}</td>)}</tr>)}</tbody></table>
      </div>)}
      {!document && <details className="mt-4 border-t border-nova-border pt-3 text-xs leading-6 text-nova-faint"><summary className="cursor-pointer rounded-md font-medium focus-visible:outline-2 focus-visible:outline-nova-accent">Xem đầy đủ thông tin</summary><div className="mt-3"><EntryLines lines={remaining} /></div><p className="mt-3 break-all">Nguồn: {entry.source}</p></details>}
      {document && <p className="mt-4 break-all border-t border-nova-border pt-3 text-xs leading-5 text-nova-faint">Nguồn: {entry.source}</p>}
    </article>
  );
}
