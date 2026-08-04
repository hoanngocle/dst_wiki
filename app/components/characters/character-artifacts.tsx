import type {
  CharacterCatalogEntry,
  CharacterGuideFact,
} from "@/app/lib/character-catalog";
import { GameSprite } from "@/app/components/game-sprite";
import { CharacterGuideFallback } from "./character-overview";

type CharacterArtifactsProps = {
  character: CharacterCatalogEntry;
};

function artifactKey(label: string, description: string): string {
  return JSON.stringify([
    label.trim().toLocaleLowerCase("vi"),
    description.trim().toLocaleLowerCase("vi"),
  ]);
}

function confidenceNote(confidence: CharacterGuideFact["confidence"]): string | null {
  if (confidence === "interpreted") return "Theo Mật Quyển";
  if (confidence === "unknown") return "Chưa rõ mốc chính xác";
  return null;
}

export function CharacterArtifacts({ character }: CharacterArtifactsProps) {
  if (character.artifacts.length === 0 && !character.guide) {
    return <CharacterGuideFallback character={character} />;
  }

  const profileKeys = new Set(
    character.artifacts.map((artifact) =>
      artifactKey(artifact.name, artifact.effect),
    ),
  );
  const guideArtifacts = character.guide?.artifacts ?? [];
  const guideOnlyArtifacts = guideArtifacts.filter(
    (artifact, index) =>
      !profileKeys.has(artifactKey(artifact.label, artifact.description)) &&
      guideArtifacts.findIndex(
        (candidate) =>
          artifactKey(candidate.label, candidate.description) ===
          artifactKey(artifact.label, artifact.description),
      ) === index,
  );
  const headingId = `character-artifacts-${character.id}`;

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
          Pháp bảo và cơ chế
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-nova-muted">
          Công dụng đã xác minh, tập trung vào quyết định trong trận.
        </p>
      </header>
      <dl className="mt-7 grid gap-5 md:grid-cols-2">
        {character.artifacts.map((artifact) => (
          <div
            key={artifact.code}
            className="flex gap-4 rounded-xl border border-nova-border bg-nova-surface-raised p-5 sm:p-6"
          >
            <GameSprite sprite={artifact.icon} size={64} />
            <div>
              <dt className="font-semibold text-nova-text">{artifact.name}</dt>
              <dd className="mt-2 text-sm leading-relaxed text-nova-muted">
                {artifact.effect}
              </dd>
            </div>
          </div>
        ))}
        {guideOnlyArtifacts.map((artifact) => {
          const note = confidenceNote(artifact.confidence);
          return (
            <div
              key={artifactKey(artifact.label, artifact.description)}
              className="rounded-xl border border-nova-border bg-nova-surface-raised p-5 sm:p-6"
            >
              <dt className="font-semibold text-nova-text">{artifact.label}</dt>
              <dd className="mt-2 text-sm leading-relaxed text-nova-muted">
                {artifact.description}
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
