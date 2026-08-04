import type {
  CharacterCatalogEntry,
  CharacterGuideFact,
} from "@/app/lib/character-catalog";
import { CharacterGuideFallback } from "./character-overview";

type CharacterCombatProps = {
  character: CharacterCatalogEntry;
};

function confidenceNote(confidence: CharacterGuideFact["confidence"]): string | null {
  if (confidence === "interpreted") return "Theo Mật Quyển";
  if (confidence === "unknown") return "Chưa rõ mốc chính xác";
  return null;
}

export function CharacterCombat({ character }: CharacterCombatProps) {
  if (!character.guide) return <CharacterGuideFallback character={character} />;

  const { guide } = character;
  const headingId = `character-combat-${character.id}`;

  return (
    <section
      aria-labelledby={headingId}
      className="rounded-2xl border border-nova-border bg-nova-surface-soft p-5 sm:p-7"
    >
      <header>
        <h2
          id={headingId}
          className="text-2xl font-semibold leading-tight tracking-tight text-nova-text"
        >
          Chiến đấu
        </h2>
        <p className="mt-4 max-w-[65ch] border-l-2 border-nova-accent pl-4 text-sm leading-relaxed text-nova-muted sm:text-base">
          {guide.attackPattern}
        </p>
      </header>
      <dl className="mt-7 grid gap-x-8 gap-y-6 sm:grid-cols-2">
        {guide.combat.map((fact) => {
          const note = confidenceNote(fact.confidence);
          return (
            <div
              key={`${fact.label}:${fact.description}`}
              className="rounded-xl border border-nova-border bg-nova-surface-raised p-4"
            >
              <dt className="font-semibold text-nova-text">{fact.label}</dt>
              <dd className="mt-2 text-sm leading-relaxed text-nova-muted">
                {fact.description}
              </dd>
              {note ? (
                <dd className="mt-3 text-xs font-semibold text-nova-accent">
                  {note}
                </dd>
              ) : null}
            </div>
          );
        })}
      </dl>
    </section>
  );
}
