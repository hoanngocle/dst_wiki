import Image from "next/image";

import type { CharacterCatalogEntry } from "@/app/lib/character-catalog";

type CharacterCardProps = {
  character: CharacterCatalogEntry;
  revealOrder?: number;
  onOpen: (character: CharacterCatalogEntry) => void;
};

const complexityLabels: Readonly<Record<string, string>> = {
  easy: "Dễ làm quen",
  medium: "Cần luyện tập",
  advanced: "Chuyên sâu",
};

const statLabels = {
  health: "Máu",
  hunger: "Đói",
  sanity: "Não",
} as const;

export function CharacterCard({
  character,
  revealOrder = 0,
  onOpen,
}: CharacterCardProps) {
  const stats = Object.entries(statLabels).flatMap(([key, label]) => {
    const stat = character.stats[key];
    return stat ? [[label, stat.display ?? stat.value] as const] : [];
  });
  const roleLine = character.guide?.roles.join(", ") ?? null;
  const complexity = character.guide?.complexity
    ? complexityLabels[character.guide.complexity] ?? null
    : null;
  const realmTeaser = character.guide?.realmMilestones[0]?.realm ?? null;

  return (
    <article
      className="catalog-card group h-full motion-safe:animate-[atlas-result-in_180ms_ease-out]"
      style={{ animationDelay: `${Math.min(revealOrder, 8) * 35}ms` }}
    >
      <button
        type="button"
        aria-label={`Mở hồ sơ ${character.name}`}
        onClick={() => onOpen(character)}
        className="group/card grid h-full min-h-11 w-full cursor-pointer grid-cols-[7rem_minmax(0,1fr)] overflow-hidden rounded-2xl border border-nova-border bg-nova-surface text-left shadow-[0_12px_28px_rgba(0,0,0,0.18)] transition-[border-color,transform,box-shadow] duration-200 hover:-translate-y-0.5 hover:border-nova-border-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent motion-reduce:transform-none motion-reduce:transition-none sm:grid-cols-[7.5rem_minmax(0,1fr)]"
      >
        <div className="p-3 pr-0">
          <div
            data-testid="character-portrait-frame"
            className="aspect-square overflow-hidden rounded-xl bg-nova-surface-soft ring-1 ring-nova-border"
          >
            <Image
              src={character.portrait}
              alt=""
              width={640}
              height={800}
              unoptimized
              loading="lazy"
              decoding="async"
              className="h-full w-full object-contain transition-transform duration-300 group-hover/card:scale-[1.035] motion-reduce:transform-none motion-reduce:transition-none"
            />
          </div>
        </div>

        <div className="flex min-w-0 flex-col p-3 sm:p-4">
          <div className="flex flex-wrap gap-1">
            <span
              data-character-chip
              className="rounded-md border border-nova-border bg-nova-surface-soft px-2 py-0.5 text-[0.6875rem] font-semibold text-nova-accent"
            >
              {character.namespace === "tu_tien" ? "Tu Tiên" : "DST"}
            </span>
            {complexity ? (
              <span
                data-character-chip
                className="rounded-md border border-nova-border bg-nova-surface-soft px-2 py-0.5 text-[0.6875rem] text-nova-muted"
              >
                {complexity}
              </span>
            ) : null}
            {realmTeaser ? (
              <span
                data-character-chip
                className="rounded-md border border-nova-border bg-nova-surface-soft px-2 py-0.5 text-[0.6875rem] text-nova-muted"
              >
                {realmTeaser}
              </span>
            ) : null}
          </div>

          <div className="mt-2.5 min-w-0">
            <h3 className="truncate text-lg font-semibold leading-tight tracking-tight text-nova-text sm:text-xl">
              {character.name}
            </h3>
            <p className="mt-0.5 truncate text-xs font-medium text-nova-muted">
              {character.title}
            </p>
          </div>

          <div className="mt-auto pt-3">
            {stats.length > 0 ? (
              <dl className="mb-2.5 grid grid-cols-3 gap-1.5">
                {stats.map(([label, value]) => (
                  <div
                    key={label}
                    className="rounded-md border border-nova-border bg-nova-surface-soft px-1.5 py-1 text-center"
                  >
                    <dt className="text-[0.58rem] font-semibold uppercase tracking-wide text-nova-faint">
                      {label}
                    </dt>
                    <dd className="text-xs font-semibold text-nova-text">
                      {value ?? "—"}
                    </dd>
                  </div>
                ))}
              </dl>
            ) : null}
            {roleLine ? (
              <p className="truncate text-xs font-semibold text-nova-text">
                {roleLine}
              </p>
            ) : null}
            {character.guide?.attackPattern ? (
              <p className="mt-1.5 line-clamp-2 border-l-2 border-nova-accent pl-2.5 text-xs leading-5 text-nova-muted">
                {character.guide.attackPattern}
              </p>
            ) : null}
          </div>
        </div>
      </button>
    </article>
  );
}
