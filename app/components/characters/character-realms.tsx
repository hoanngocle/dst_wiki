import type {
  CharacterCatalogEntry,
  CharacterGuideFact,
} from "@/app/lib/character-catalog";
import { CharacterGuideFallback } from "./character-overview";

type CharacterRealmsProps = {
  character: CharacterCatalogEntry;
};

function confidenceNote(confidence: CharacterGuideFact["confidence"]): string | null {
  if (confidence === "interpreted") return "Theo Mật Quyển";
  if (confidence === "unknown") return "Chưa rõ mốc chính xác";
  return null;
}

function isUncertainRealm(realm: string): boolean {
  return realm.toLocaleLowerCase("vi").includes("chưa");
}

export function CharacterRealms({ character }: CharacterRealmsProps) {
  if (!character.guide) return <CharacterGuideFallback character={character} />;

  const partitioned = character.guide.realmMilestones.map((milestone) => {
    const uncertainLabel = isUncertainRealm(milestone.realm);
    return {
      realm: milestone.realm,
      confirmed: uncertainLabel
        ? []
        : milestone.unlocks.filter((unlock) => unlock.confidence !== "unknown"),
      uncertain: uncertainLabel
        ? milestone.unlocks
        : milestone.unlocks.filter((unlock) => unlock.confidence === "unknown"),
    };
  });
  const timeline = partitioned.filter((milestone) => milestone.confirmed.length > 0);
  const uncertain = partitioned.filter((milestone) => milestone.uncertain.length > 0);
  const headingId = `character-realms-${character.id}`;

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
          Tiến triển cảnh giới
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-nova-muted">
          Các mốc giữ nguyên thứ tự từ nguồn đã xác minh.
        </p>
      </header>
      <ol
        data-testid="realm-timeline"
        className="mt-7 space-y-6 border-l-2 border-nova-border pl-6 sm:pl-8"
      >
        {timeline.length > 0 ? (
          timeline.map((milestone) => (
            <li key={milestone.realm} className="relative">
              <span
                aria-hidden="true"
                className="absolute -left-[1.95rem] top-1.5 h-3 w-3 rotate-45 rounded-sm bg-nova-accent ring-4 ring-nova-bg sm:-left-[2.45rem]"
              />
              <h3 className="text-lg font-semibold text-nova-text">
                {milestone.realm}
              </h3>
              <div className="mt-3 space-y-4">
                {milestone.confirmed.map((unlock) => {
                  const note = confidenceNote(unlock.confidence);
                  return (
                    <article
                      key={`${unlock.label}:${unlock.description}`}
                      className="rounded-xl bg-nova-surface-raised p-4 ring-1 ring-nova-border"
                    >
                      <h4 className="font-semibold text-nova-text">{unlock.label}</h4>
                      <p className="mt-1.5 text-sm leading-relaxed text-nova-muted">
                        {unlock.description}
                      </p>
                      {note ? (
                        <p className="mt-2 text-xs font-semibold text-nova-accent">
                          {note}
                        </p>
                      ) : null}
                    </article>
                  );
                })}
              </div>
            </li>
          ))
        ) : (
          <li className="text-sm leading-relaxed text-nova-muted">
            Chưa có mốc cảnh giới được xác nhận.
          </li>
        )}
      </ol>

      {uncertain.length > 0 ? (
        <aside
          data-testid="realm-unknown-notes"
          aria-label="Các mốc chưa thể xác định"
          className="mt-8 rounded-xl border border-nova-border bg-nova-surface-raised p-5 sm:p-6"
        >
          <h3 className="font-semibold text-nova-text">Phần chưa thể xác định</h3>
          <div className="mt-4 space-y-5">
            {uncertain.map((milestone) => (
              <section key={milestone.realm}>
                <h4 className="font-semibold text-nova-text">{milestone.realm}</h4>
                <div className="mt-2 space-y-3">
                  {milestone.uncertain.map((unlock) => (
                    <div key={`${unlock.label}:${unlock.description}`}>
                      <p className="text-sm font-semibold text-nova-text">
                        {unlock.label}
                      </p>
                      <p className="mt-1 text-sm leading-relaxed text-nova-muted">
                        {unlock.description}
                      </p>
                      <p className="mt-2 text-xs font-semibold text-nova-accent">
                        {confidenceNote(unlock.confidence)}
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            ))}
          </div>
        </aside>
      ) : null}
    </section>
  );
}
