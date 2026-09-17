import { ClipboardText, Medal } from "@phosphor-icons/react";
import { GameSprite } from "@/app/components/game-sprite";
import { guildQuestDifficulty, type SoloLevelingEntry } from "@/app/lib/solo-leveling";

const difficultyStyles = {
  "Dễ": { row: "border-emerald-200 border-l-emerald-500 bg-emerald-50/70", badge: "border-emerald-200 bg-emerald-100 text-emerald-800", icon: "text-emerald-700" },
  "Vừa": { row: "border-amber-200 border-l-amber-500 bg-amber-50/70", badge: "border-amber-200 bg-amber-100 text-amber-900", icon: "text-amber-700" },
  "Khó": { row: "border-rose-200 border-l-rose-500 bg-rose-50/70", badge: "border-rose-200 bg-rose-100 text-rose-800", icon: "text-rose-700" },
};
const rankStyle = { row: "border-nova-border border-l-nova-accent bg-nova-surface-soft", badge: "border-nova-accent/20 bg-nova-accent/10 text-nova-accent", icon: "text-nova-accent" };
const rankStyles = {
  E: { row: "border-slate-200 border-l-slate-500 bg-slate-50/70", badge: "border-slate-200 bg-slate-100 text-slate-700", icon: "text-slate-600" },
  D: difficultyStyles["Dễ"],
  C: { row: "border-sky-200 border-l-sky-500 bg-sky-50/70", badge: "border-sky-200 bg-sky-100 text-sky-800", icon: "text-sky-700" },
  B: { row: "border-violet-200 border-l-violet-500 bg-violet-50/70", badge: "border-violet-200 bg-violet-100 text-violet-800", icon: "text-violet-700" },
  A: difficultyStyles["Vừa"],
  S: difficultyStyles["Khó"],
};

export function SoloLevelingQuestRow({ entry, topic }: { entry: SoloLevelingEntry; topic: "daily" | "guild" | "exams" }) {
  const daily = topic === "daily";
  const difficulty = (topic === "guild" ? guildQuestDifficulty(entry.rank) : daily ? entry.category : undefined) as keyof typeof difficultyStyles | undefined;
  const colors = topic === "exams" ? rankStyles[entry.rank as keyof typeof rankStyles] ?? rankStyle : difficulty ? difficultyStyles[difficulty] ?? rankStyle : rankStyle;
  const Icon = topic === "exams" ? Medal : ClipboardText;
  const description = entry.lines[0];
  const objective = entry.lines.find((line) => line.startsWith("Mục tiêu:"));
  const reward = entry.lines.find((line) => /^\d+ EXP$/.test(line) || line.startsWith("Xu Hiệp Hội:"));
  const badge = entry.lines.find((line) => line.startsWith(daily ? "Độ khó:" : "Rank:"));
  const remaining = entry.lines.filter((line) => ![description, objective, reward, badge].includes(line));

  return (
    <article id={entry.id} aria-labelledby={`${entry.id}-title`} data-rank={entry.rank} data-difficulty={difficulty} className={`min-w-0 scroll-mt-6 rounded-xl border border-l-4 p-4 ${colors.row}`}>
      <div className="grid items-center gap-4 sm:grid-cols-[minmax(0,1fr)_6rem_8rem]">
        <div className="flex min-w-0 items-start gap-3">
          <Icon size={28} weight="duotone" aria-hidden="true" className={`mt-1 shrink-0 ${colors.icon}`} />
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
              <h3 id={`${entry.id}-title`} className="text-base font-semibold leading-6 [overflow-wrap:anywhere]">{entry.title}</h3>
              {badge && <span className={`rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ${colors.badge}`}>{badge}</span>}
              {topic === "guild" && difficulty && <span className={`rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ${colors.badge}`}>Nhóm: {difficulty}</span>}
            </div>
            <p className="mt-1.5 text-sm leading-6 text-nova-muted [overflow-wrap:anywhere]">{description}</p>
          </div>
        </div>
        <div className="ml-10 flex items-center justify-between gap-4 sm:ml-0 sm:block">
          <p className="text-xs text-nova-faint">Yêu cầu</p>
          <p className="text-sm font-semibold leading-6 sm:mt-1">{objective}</p>
        </div>
        <div className="ml-10 flex items-center justify-between gap-4 sm:ml-0 sm:block">
          <p className="text-xs text-nova-faint">Phần thưởng</p>
          <p className="text-sm font-semibold leading-6 text-nova-accent sm:mt-1">{reward?.startsWith("Xu Hiệp Hội:") ? `${reward.slice("Xu Hiệp Hội: ".length)} Xu Hiệp Hội` : reward}</p>
        </div>
      </div>
      <details className="mt-3 border-t border-current/10 pt-3 text-xs leading-6 text-nova-muted sm:ml-10">
        <summary className="w-fit cursor-pointer rounded-md font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-nova-accent">{daily ? "Cách tính tiến độ & điều kiện" : "Điều kiện & phần thưởng"}</summary>
        <div className="mt-2 space-y-2 text-sm">{remaining.map((line, index) => <p key={index} className="whitespace-pre-line [overflow-wrap:anywhere]">{line}</p>)}</div>
        {entry.related && <div className="mt-3 flex flex-wrap gap-2">{entry.related.map((target) => <GameSprite key={target.prefab} sprite={target.sprite} size={40} label={`Mục tiêu ${target.name}`} />)}</div>}
        <p className="mt-3 break-all text-xs text-nova-faint">Nguồn: {entry.source}</p>
      </details>
    </article>
  );
}
