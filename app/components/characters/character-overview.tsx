import type { CharacterCatalogEntry } from "@/app/lib/character-catalog";
import { GameSprite } from "@/app/components/game-sprite";

type CharacterSectionProps = {
  character: CharacterCatalogEntry;
};

export function CharacterGuideFallback({ character }: CharacterSectionProps) {
  return (
    <section
      aria-label={`Hồ sơ cơ bản ${character.name}`}
      className="rounded-2xl border border-nova-border bg-nova-surface-soft p-6 sm:p-8"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-nova-accent">
        Hồ sơ cơ bản
      </p>
      <h2 className="mt-2 text-xl font-semibold leading-tight tracking-tight text-nova-text sm:text-2xl">
        {character.title || character.name}
      </h2>
      <p className="mt-3 max-w-[65ch] text-sm leading-relaxed text-nova-muted sm:text-base">
        {character.description}
      </p>
      <p className="mt-5 rounded-xl border border-nova-border bg-nova-surface-raised p-4 text-sm leading-relaxed text-nova-muted">
        Nhân vật này chưa có hướng dẫn chiến thuật; các thông tin hồ sơ đã xác minh vẫn được giữ nguyên.
      </p>
    </section>
  );
}

export function CharacterOverview({ character }: CharacterSectionProps) {
  const { guide } = character;
  const headingId = `character-overview-${character.id}`;

  if (!guide && character.abilities.length === 0 && character.startingItems.length === 0) {
    return <CharacterGuideFallback character={character} />;
  }

  return (
    <section
      aria-labelledby={headingId}
      className="space-y-7 rounded-2xl border border-nova-border bg-nova-surface-soft p-5 sm:p-7"
    >
      <header>
        <h2
          id={headingId}
          className="text-2xl font-semibold leading-tight tracking-tight text-nova-text"
        >
          Tổng quan
        </h2>
        <p className="mt-3 max-w-[65ch] text-sm leading-relaxed text-nova-muted sm:text-base">
          {guide?.summary ?? character.description}
        </p>
      </header>

      {!guide ? (
        <div className="rounded-xl border border-nova-border bg-nova-surface-raised p-4">
          <p className="font-semibold text-nova-text">Hồ sơ cơ bản</p>
          <p className="mt-1 text-sm leading-relaxed text-nova-muted">
            Nhân vật này chưa có hướng dẫn chiến thuật; phần dưới chỉ hiển thị dữ liệu hồ sơ đã xác minh.
          </p>
        </div>
      ) : null}

      {character.abilities.length > 0 ? (
        <section>
          <h3 className="text-lg font-semibold text-nova-text">Năng lực đặc biệt</h3>
          <dl className="mt-4 grid gap-4 md:grid-cols-2">
            {character.abilities.map((ability) => (
              <div
                key={`${ability.name}:${ability.effect}`}
                className="rounded-xl border border-nova-border bg-nova-surface-raised p-5"
              >
                <dt className="font-semibold text-nova-text">{ability.name}</dt>
                <dd className="mt-2 text-sm leading-relaxed text-nova-muted">
                  {ability.effect}
                </dd>
              </div>
            ))}
          </dl>
        </section>
      ) : null}

      {character.startingItems.length > 0 ? (
        <section className="border-t border-nova-border pt-6">
          <h3 className="text-lg font-semibold text-nova-text">Vật phẩm khởi đầu</h3>
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {character.startingItems.map((item) => (
              <li
                key={item.code}
                className="flex gap-3 rounded-xl border border-nova-border bg-nova-surface-raised p-4"
              >
                <GameSprite sprite={item.icon} size={48} />
                <div>
                  <p className="font-semibold text-nova-text">
                    {item.name}
                    {item.quantity !== null && item.quantity > 1
                      ? ` ×${item.quantity}`
                      : ""}
                  </p>
                  <p className="mt-1 text-sm leading-relaxed text-nova-muted">
                    {item.effect}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {guide ? (
        <div className="grid gap-5 md:grid-cols-2">
          <section className="rounded-xl border border-nova-border bg-nova-surface-raised p-5 sm:p-6">
            <h3 className="font-semibold text-nova-text">Điểm mạnh</h3>
            <ul className="mt-4 space-y-3">
              {guide.strengths.map((strength) => (
                <li
                  key={strength}
                  className="border-l-2 border-nova-accent pl-3 text-sm leading-relaxed text-nova-muted"
                >
                  {strength}
                </li>
              ))}
            </ul>
          </section>
          <section className="rounded-xl border border-nova-border bg-nova-surface-raised p-5 sm:p-6">
            <h3 className="font-semibold text-nova-text">Đổi lại</h3>
            <ul className="mt-4 space-y-3">
              {guide.tradeoffs.map((tradeoff) => (
                <li
                  key={tradeoff}
                  className="border-l-2 border-nova-border pl-3 text-sm leading-relaxed text-nova-muted"
                >
                  {tradeoff}
                </li>
              ))}
            </ul>
          </section>
        </div>
      ) : null}

      {guide ? (
        <section className="border-t border-nova-border pt-6">
          <h3 className="text-lg font-semibold text-nova-text">Khởi đầu nên làm</h3>
          <ol className="mt-4 grid gap-4 sm:grid-cols-2">
            {guide.firstSteps.map((step) => (
              <li
                key={step}
                className="rounded-xl bg-nova-surface-raised p-4 text-sm leading-relaxed text-nova-text ring-1 ring-nova-border"
              >
                {step}
              </li>
            ))}
          </ol>
        </section>
      ) : null}
    </section>
  );
}
