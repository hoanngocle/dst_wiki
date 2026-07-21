import type {
  CatalogMobDetails,
  CategoryMobDetails,
  ItemDetailStatus,
  ItemListEntry,
  ItemReference,
  MobSection,
  MobStat,
  MobRewardMethod,
  MobVariant,
} from "@/app/lib/item-catalog";
import { useState } from "react";
import { GameSprite } from "./game-sprite";

const METHOD_LABEL: Record<MobRewardMethod, string> = {
  kill: "Rơi khi tiêu diệt",
  mine_post_defeat: "Khai thác xác bằng cuốc",
  harvest: "Thu hoạch",
  conditional: "Phần thưởng có điều kiện",
};

const ROLE_LABEL: Record<MobVariant["role"], string> = {
  phase: "Giai đoạn",
  variant: "Biến thể",
  summon: "Sinh vật được triệu hồi",
  post_defeat: "Giai đoạn hậu chiến",
};

function Section({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section
      aria-labelledby={id}
      className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]"
    >
      <h3
        id={id}
        className="border-b border-[#d5dde6] px-4 py-3 text-sm font-semibold text-[#172943]"
      >
        {title}
      </h3>
      {children}
    </section>
  );
}

function StatusMessage({
  status,
  noneText,
}: {
  status: ItemDetailStatus;
  noneText: string;
}) {
  return (
    <p className="px-4 py-4 text-sm leading-6 text-[#607188]">
      {status === "none" ? noneText : "Chưa xác minh được dữ liệu từ mã game hoặc Wiki."}
    </p>
  );
}

function ReferenceButton({
  reference,
  itemsById,
  onSelectItem,
}: {
  reference: ItemReference;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  const target = itemsById.get(reference.id);
  const content = (
    <>
      <GameSprite sprite={target?.sprite ?? reference.sprite} size={40} />
      <span>{target?.name ?? reference.name}</span>
    </>
  );
  if (!target) {
    return <span className="inline-flex items-center gap-2 font-semibold">{content}</span>;
  }
  return (
    <button
      type="button"
      aria-label={target.name}
      onClick={() => onSelectItem(target)}
      className="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-xl px-2 py-1 font-semibold text-[#263b58] transition hover:bg-[#e9f1fb] hover:text-[#2e5fb3] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/30"
    >
      {content}
    </button>
  );
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 4 }).format(value);
}

function formatStat(value: string | number, unit: string | null): string {
  const formatted = typeof value === "number" ? formatNumber(value) : value;
  return `${formatted}${unit && unit !== "hp" ? ` ${unit}` : ""}`;
}

function formatQuantity(minimum: number, maximum: number): string {
  return minimum === maximum
    ? `×${formatNumber(minimum)}`
    : `×${formatNumber(minimum)}–${formatNumber(maximum)}`;
}

function sourceName(details: CatalogMobDetails, sourceVariant: string | null): string {
  if (sourceVariant === null) return "Dùng chung";
  return details.variants.find((variant) => variant.id === sourceVariant)?.name ?? sourceVariant;
}

function AppearanceSection({ details, titleId }: { details: CatalogMobDetails; titleId: string }) {
  const appearance = details.appearance;
  return (
    <Section id={`${titleId}-appearance`} title="Xuất hiện">
      {appearance.status === "known" ? (
        <div className="space-y-3 p-4 text-sm leading-6 text-[#43556d]">
          {appearance.sources.length ? (
            <ul className="list-disc space-y-1 pl-5">
              {appearance.sources.map((source) => <li key={source}>{source}</li>)}
            </ul>
          ) : null}
          <dl className="grid gap-3 sm:grid-cols-2">
            <div>
              <dt className="text-xs font-semibold uppercase tracking-[0.06em] text-[#607188]">Spawn code</dt>
              <dd className="mt-1 break-words">{appearance.spawnCodes.join(", ")}</dd>
            </div>
            {appearance.renewable !== null ? (
              <div>
                <dt className="text-xs font-semibold uppercase tracking-[0.06em] text-[#607188]">Tái tạo</dt>
                <dd className="mt-1">{appearance.renewable ? "Có" : "Không"}</dd>
              </div>
            ) : null}
            {appearance.respawn !== null ? (
              <div>
                <dt className="text-xs font-semibold uppercase tracking-[0.06em] text-[#607188]">Hồi sinh</dt>
                <dd className="mt-1">{appearance.respawn}</dd>
              </div>
            ) : null}
          </dl>
          {appearance.wikiUrl ? (
            <a
              href={appearance.wikiUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex font-semibold text-[#2e5fb3] underline decoration-[#9bb8df] underline-offset-4"
            >
              Xem nguồn Wiki
            </a>
          ) : null}
        </div>
      ) : (
        <StatusMessage status={appearance.status} noneText="Không có nguồn xuất hiện." />
      )}
    </Section>
  );
}

function VariantSection({ details, titleId }: { details: CatalogMobDetails; titleId: string }) {
  return (
    <Section id={`${titleId}-variants`} title="Giai đoạn / biến thể">
      {details.variants.length ? (
        <ul className="grid gap-2 p-4 sm:grid-cols-2">
          {details.variants.map((variant) => (
            <li key={variant.id} className="flex items-center gap-3 rounded-xl border border-[#d5dde6] bg-white p-3">
              <GameSprite sprite={variant.sprite} size={40} />
              <div className="min-w-0">
                <p className="truncate font-semibold text-[#263b58]">{variant.name}</p>
                <p className="text-xs text-[#607188]">{ROLE_LABEL[variant.role]}</p>
                <code className="text-[11px] text-[#738298]">{variant.prefabId}</code>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="px-4 py-4 text-sm leading-6 text-[#607188]">Chưa xác minh được biến thể.</p>
      )}
    </Section>
  );
}

function CatalogMobSections({
  item,
  itemsById,
  onSelectItem,
  titleId,
}: {
  item: ItemListEntry;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
  titleId: string;
}) {
  const details = item.mob;
  if (!details || details.contract !== "catalog") {
    return (
      <Section id={`${titleId}-mob-data`} title="Dữ liệu Mob / Boss">
        <p className="px-4 py-4 text-sm leading-6 text-[#607188]">
          Chưa xác minh được dữ liệu từ mã game hoặc Wiki.
        </p>
      </Section>
    );
  }

  return (
    <>
      <AppearanceSection details={details} titleId={titleId} />
      <VariantSection details={details} titleId={titleId} />
      <Section id={`${titleId}-stats`} title="Chỉ số">
        {details.stats.length ? (
          <dl className="grid grid-cols-2 gap-px bg-[#d5dde6] sm:grid-cols-3">
            {details.stats.map((stat) => (
              <div key={`${stat.sourceVariant}:${stat.key}`} className="bg-white px-4 py-3">
                <dt className="text-xs font-semibold text-[#607188]">{stat.label}</dt>
                <dd className="mt-1 text-lg font-semibold text-[#172943]">
                  {formatStat(stat.value, stat.unit)}
                </dd>
                <p className="mt-1 text-[11px] text-[#738298]">{sourceName(details, stat.sourceVariant)}</p>
              </div>
            ))}
          </dl>
        ) : (
          <p className="px-4 py-4 text-sm leading-6 text-[#607188]">Chưa xác minh được chỉ số.</p>
        )}
      </Section>
      <Section id={`${titleId}-mechanics`} title="Kỹ năng / cơ chế đặc biệt">
        {details.mechanics.length ? (
          <ul className="space-y-2 p-4">
            {details.mechanics.map((mechanic) => (
              <li key={`${mechanic.sourceVariant}:${mechanic.text}`} className="rounded-xl border border-[#d5dde6] bg-white px-3 py-2.5 text-sm leading-6 text-[#43556d]">
                <p>{mechanic.text}</p>
                <p className="mt-1 text-xs text-[#738298]">{sourceName(details, mechanic.sourceVariant)}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="px-4 py-4 text-sm leading-6 text-[#607188]">Chưa xác minh được cơ chế riêng.</p>
        )}
      </Section>
      <Section id={`${titleId}-loot`} title="Vật phẩm có thể thu được">
        {details.lootStatus === "known" ? (
          <ul className="space-y-2 p-4">
            {details.loot.map((reward) => (
              <li key={`${reward.sourceVariant}:${reward.method}:${reward.item.id}`} className="grid gap-2 rounded-xl border border-[#d5dde6] bg-white p-3 text-sm sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
                <div>
                  <ReferenceButton reference={reward.item} itemsById={itemsById} onSelectItem={onSelectItem} />
                  <p className="ml-2 text-xs font-semibold text-[#2e5fb3]">{METHOD_LABEL[reward.method]}</p>
                  <p className="ml-2 text-xs text-[#607188]">Nguồn: {sourceName(details, reward.sourceVariant)}</p>
                  {reward.conditions ? <p className="ml-2 text-xs text-[#607188]">{reward.conditions}</p> : null}
                </div>
                <div className="flex gap-2 text-xs font-semibold">
                  <span className="rounded-lg bg-[#eef3f8] px-2 py-1">{formatQuantity(reward.minimum, reward.maximum)}</span>
                  {reward.chance ? <span className="rounded-lg bg-[#e9f1fb] px-2 py-1 text-[#2e5fb3]">{reward.chance}</span> : null}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <StatusMessage status={details.lootStatus} noneText="Không có vật phẩm thu được." />
        )}
      </Section>
    </>
  );
}

function visibleForVariant<T extends { sourceVariant: string | null }>(
  values: readonly T[],
  selectedCode: string,
): readonly T[] {
  return values.filter(
    (value) => value.sourceVariant === null || value.sourceVariant === selectedCode,
  );
}

function CategoryFactSection({
  id,
  title,
  section,
  selectedCode,
}: {
  id: string;
  title: string;
  section: MobSection<MobStat>;
  selectedCode: string;
}) {
  if (section.status === "none") return null;
  const values = visibleForVariant(section.values, selectedCode);
  return (
    <Section id={id} title={title}>
      {section.status === "unknown" || !values.length ? (
        <p className="px-4 py-4 text-sm text-[#607188]">Chưa xác minh</p>
      ) : (
        <dl className="grid grid-cols-2 gap-px bg-[#d5dde6] sm:grid-cols-3">
          {values.map((stat) => (
            <div key={`${stat.sourceVariant ?? "shared"}:${stat.key}`} className="bg-white px-4 py-3">
              <dt className="text-xs font-semibold text-[#607188]">{stat.label}</dt>
              <dd className="mt-1 text-lg font-semibold text-[#172943]">
                {formatStat(stat.value, stat.unit)}
              </dd>
            </div>
          ))}
        </dl>
      )}
    </Section>
  );
}

function CategoryMobSections({
  details,
  itemsById,
  onSelectItem,
  titleId,
}: {
  details: CategoryMobDetails;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
  titleId: string;
}) {
  const [selectedCode, setSelectedCode] = useState(details.identity.primaryCode);

  const traits = visibleForVariant(details.traits.values, selectedCode);
  const loot = visibleForVariant(details.loot.values, selectedCode);
  const spawnSources = visibleForVariant(details.spawnsFrom.values, selectedCode);

  return (
    <>
      {details.variants.length > 1 ? (
        <div
          role="tablist"
          aria-label="Mob variants"
          className="flex flex-wrap gap-2 rounded-2xl border border-[#c8d3df] bg-[#f8fafc] p-3"
        >
          {details.variants.map((variant) => (
            <button
              key={variant.code}
              type="button"
              role="tab"
              aria-selected={selectedCode === variant.code}
              onClick={() => setSelectedCode(variant.code)}
              className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-[#c8d3df] bg-white px-3 text-sm font-semibold text-[#263b58] aria-selected:border-[#2e5fb3] aria-selected:bg-[#e9f1fb] aria-selected:text-[#2e5fb3]"
            >
              <GameSprite sprite={variant.sprite} size={28} />
              {variant.label}
            </button>
          ))}
        </div>
      ) : null}

      <CategoryFactSection id={`${titleId}-stats`} title="Stats" section={details.stats} selectedCode={selectedCode} />
      <CategoryFactSection id={`${titleId}-effects`} title="Effects" section={details.effects} selectedCode={selectedCode} />
      <CategoryFactSection id={`${titleId}-combat`} title="Combat" section={details.combat} selectedCode={selectedCode} />
      <CategoryFactSection id={`${titleId}-movement`} title="Movement" section={details.movement} selectedCode={selectedCode} />

      {details.traits.status !== "none" ? (
        <Section id={`${titleId}-traits`} title="Traits">
          {details.traits.status === "unknown" || !traits.length ? (
            <p className="px-4 py-4 text-sm text-[#607188]">Chưa xác minh</p>
          ) : (
            <ul className="space-y-2 p-4 text-sm leading-6 text-[#43556d]">
              {traits.map((trait) => (
                <li key={`${trait.sourceVariant ?? "shared"}:${trait.text}`} className="rounded-xl border border-[#d5dde6] bg-white px-3 py-2.5">
                  {trait.text}
                </li>
              ))}
            </ul>
          )}
        </Section>
      ) : null}

      {details.loot.status !== "none" ? (
        <Section id={`${titleId}-loot`} title="Loot">
          {details.loot.status === "unknown" || !loot.length ? (
            <p className="px-4 py-4 text-sm text-[#607188]">Chưa xác minh</p>
          ) : (
            <ul className="space-y-2 p-4">
              {loot.map((reward) => (
                <li key={`${reward.sourceVariant ?? "shared"}:${reward.method}:${reward.item.id}`} className="grid gap-2 rounded-xl border border-[#d5dde6] bg-white p-3 text-sm sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
                  <div>
                    <ReferenceButton reference={reward.item} itemsById={itemsById} onSelectItem={onSelectItem} />
                    <p className="ml-2 text-xs font-semibold text-[#2e5fb3]">{METHOD_LABEL[reward.method]}</p>
                    {reward.conditions ? <p className="ml-2 text-xs text-[#607188]">{reward.conditions}</p> : null}
                  </div>
                  <div className="flex gap-2 text-xs font-semibold">
                    <span className="rounded-lg bg-[#eef3f8] px-2 py-1">{reward.quantity}</span>
                    {reward.chance ? <span className="rounded-lg bg-[#e9f1fb] px-2 py-1 text-[#2e5fb3]">{reward.chance}</span> : null}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Section>
      ) : null}

      {details.spawnsFrom.status !== "none" ? (
        <Section id={`${titleId}-spawns-from`} title="Spawns from">
          {details.spawnsFrom.status === "unknown" || !spawnSources.length ? (
            <p className="px-4 py-4 text-sm text-[#607188]">Chưa xác minh</p>
          ) : (
            <ul className="space-y-2 p-4">
              {spawnSources.map((spawn) => (
                <li key={`${spawn.sourceVariant ?? "shared"}:${spawn.source.id}`}>
                  <ReferenceButton reference={spawn.source} itemsById={itemsById} onSelectItem={onSelectItem} />
                  {spawn.conditions ? <p className="ml-2 text-xs text-[#607188]">{spawn.conditions}</p> : null}
                </li>
              ))}
            </ul>
          )}
        </Section>
      ) : null}

      {details.notes.status !== "none" ? (
        <Section id={`${titleId}-notes`} title="Notes">
          {details.notes.status === "unknown" ? (
            <p className="px-4 py-4 text-sm text-[#607188]">Chưa xác minh</p>
          ) : (
            <ul className="space-y-2 p-4 text-sm leading-6 text-[#43556d]">
              {details.notes.values.map((note) => <li key={note.sourceSha256}>{note.summaryVi}</li>)}
            </ul>
          )}
        </Section>
      ) : null}

      <Section id={`${titleId}-code`} title="Code">
        <code className="block break-words px-4 py-4 text-sm text-[#43556d]">
          {details.identity.prefabCodes.join(", ")}
        </code>
      </Section>
      <Section id={`${titleId}-source`} title="Source">
        <a
          href={details.identity.sourceUrl}
          target="_blank"
          rel="noreferrer"
          className="block break-words px-4 py-4 text-sm font-semibold text-[#2e5fb3] underline decoration-[#9bb8df] underline-offset-4"
        >
          Fandom · revision {details.identity.revisionId}
        </a>
      </Section>
    </>
  );
}

export function MobSections({
  item,
  itemsById,
  onSelectItem,
  titleId,
}: {
  item: ItemListEntry;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
  titleId: string;
}) {
  if (!item.mob) {
    return (
      <Section id={`${titleId}-mob-data`} title="Dữ liệu Mob / Boss">
        <p className="px-4 py-4 text-sm leading-6 text-[#607188]">Chưa xác minh</p>
      </Section>
    );
  }
  if (item.mob.contract === "category") {
    return (
      <CategoryMobSections
        key={item.id}
        details={item.mob}
        itemsById={itemsById}
        onSelectItem={onSelectItem}
        titleId={titleId}
      />
    );
  }
  return (
    <CatalogMobSections
      item={item}
      itemsById={itemsById}
      onSelectItem={onSelectItem}
      titleId={titleId}
    />
  );
}
