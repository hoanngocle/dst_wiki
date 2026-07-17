import Image from "next/image";

import type {
  ItemDetailStatus,
  ItemListEntry,
  ItemReference,
  StructureDetails,
} from "@/app/lib/item-catalog";
import { GameSprite } from "./game-sprite";
import { RecipeIngredients } from "./recipe-ingredients";

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
  reason,
  noneText,
}: {
  status: ItemDetailStatus;
  reason?: string | null;
  noneText: string;
}) {
  return (
    <p className="px-4 py-4 text-sm leading-6 text-[#607188]">
      {reason ?? (status === "none" ? noneText : "Chưa xác minh đủ dữ liệu.")}
    </p>
  );
}

function FactGrid({
  rows,
}: {
  rows: readonly { label: string; value: React.ReactNode }[];
}) {
  const visible = rows.filter((row) => row.value !== null && row.value !== "");
  if (!visible.length) return null;
  return (
    <dl className="grid gap-x-5 gap-y-3 p-4 text-sm sm:grid-cols-2">
      {visible.map((row) => (
        <div key={row.label} className="min-w-0">
          <dt className="text-xs font-semibold uppercase tracking-[0.06em] text-[#607188]">
            {row.label}
          </dt>
          <dd className="mt-1 leading-6 text-[#263b58]">{row.value}</dd>
        </div>
      ))}
    </dl>
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

function OriginSection({ details, titleId }: { details: StructureDetails; titleId: string }) {
  const origin = details.origin;
  return (
    <Section id={`${titleId}-origin`} title="Xuất hiện">
      <FactGrid
        rows={[
          { label: "Có thể chế tạo", value: origin.craftable ? "Có" : "Không" },
          {
            label: "Tự sinh trong thế giới",
            value: origin.naturallySpawned ? "Có" : "Không",
          },
          {
            label: "Tái tạo",
            value: origin.renewable === null ? null : origin.renewable ? "Có" : "Không",
          },
          { label: "Spawn code", value: origin.spawnCode },
          { label: "Hồi sinh", value: origin.respawn },
        ]}
      />
      {origin.sources.length ? (
        <ul className="border-t border-[#dce3eb] px-4 py-3 text-sm leading-6 text-[#43556d]">
          {origin.sources.map((source) => <li key={source}>{source}</li>)}
        </ul>
      ) : null}
      {origin.note ? (
        <p className="border-t border-[#dce3eb] px-4 py-3 text-sm leading-6 text-[#53647a]">
          {origin.note}
        </p>
      ) : null}
    </Section>
  );
}

function ConstructionSection({
  details,
  titleId,
  itemsById,
  onSelectItem,
}: {
  details: StructureDetails;
  titleId: string;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  const construction = details.construction;
  return (
    <Section id={`${titleId}-construction`} title="Công thức xây dựng">
      {construction.status === "known" ? (
        <>
          <div className="p-4">
            <RecipeIngredients
              recipe={{
                outputCount: construction.outputCount ?? 1,
                ingredients: construction.ingredients,
              }}
              itemsById={itemsById}
              onSelectItem={onSelectItem}
            />
          </div>
          <FactGrid
            rows={[
              { label: "Cấp công nghệ", value: construction.tech },
              { label: "Công trình yêu cầu", value: construction.station },
              { label: "Số lượng tạo ra", value: construction.outputCount },
            ]}
          />
          {construction.note ? (
            <p className="border-t border-[#dce3eb] px-4 py-3 text-sm leading-6 text-[#53647a]">
              {construction.note}
            </p>
          ) : null}
        </>
      ) : (
        <StatusMessage
          status={construction.status}
          reason={construction.note}
          noneText="Không thể chế tạo."
        />
      )}
    </Section>
  );
}

function FunctionsSection({ details, titleId }: { details: StructureDetails; titleId: string }) {
  const section = details.functions;
  return (
    <Section id={`${titleId}-functions`} title="Công dụng">
      {section.status === "known" && section.facts.length ? (
        <ul className="grid gap-3 p-4 sm:grid-cols-2">
          {section.facts.map((fact) => (
            <li key={fact.key} className="rounded-xl border border-[#d5dde6] bg-white p-3">
              <p className="text-xs font-semibold uppercase tracking-[0.06em] text-[#607188]">
                {fact.label}
              </p>
              <p className="mt-1 text-sm font-semibold text-[#263b58]">
                {fact.value}{fact.unit ? ` ${fact.unit}` : ""}
              </p>
              {fact.context ? <p className="mt-1 text-xs text-[#607188]">{fact.context}</p> : null}
            </li>
          ))}
        </ul>
      ) : (
        <StatusMessage status={section.status} reason={section.reason} noneText="Không có công dụng riêng." />
      )}
    </Section>
  );
}

function CraftablesSection({
  details,
  titleId,
  itemsById,
  onSelectItem,
}: {
  details: StructureDetails;
  titleId: string;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  const section = details.craftables;
  return (
    <Section id={`${titleId}-craftables`} title="Vật phẩm chế tạo tại công trình">
      {section.status === "known" && section.recipes.length ? (
        <ul className="space-y-3 p-4">
          {section.recipes.map((recipe) => (
            <li key={recipe.result.id} className="rounded-xl border border-[#d5dde6] bg-white p-3">
              <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
                <ReferenceButton
                  reference={recipe.result}
                  itemsById={itemsById}
                  onSelectItem={onSelectItem}
                />
                {recipe.resultAmount > 1 ? <span>×{recipe.resultAmount}</span> : null}
              </div>
              {recipe.ingredients.length ? (
                <div className="mt-2">
                  <RecipeIngredients
                    recipe={{ outputCount: recipe.resultAmount, ingredients: recipe.ingredients }}
                    itemsById={itemsById}
                    onSelectItem={onSelectItem}
                  />
                </div>
              ) : null}
              {recipe.tech ? <p className="mt-2 text-xs text-[#607188]">{recipe.tech}</p> : null}
            </li>
          ))}
        </ul>
      ) : (
        <StatusMessage
          status={section.status}
          reason={section.reason}
          noneText="Không có vật phẩm riêng cần chế tạo tại công trình này."
        />
      )}
    </Section>
  );
}

function DestructionSection({ details, titleId }: { details: StructureDetails; titleId: string }) {
  const section = details.destruction;
  return (
    <Section id={`${titleId}-destruction`} title="Phá huỷ và thu hồi">
      {section.status === "known" ? (
        <FactGrid
          rows={[
            {
              label: "Có thể phá huỷ",
              value: section.destroyable === null ? null : section.destroyable ? "Có" : "Không",
            },
            { label: "Công cụ", value: section.tool },
            { label: "Số lần tác động", value: section.work },
            { label: "Độ bền", value: section.health },
            {
              label: "Có thể cháy",
              value: section.burnable === null ? null : section.burnable ? "Có" : "Không",
            },
            { label: "Tái sinh", value: section.regeneration },
          ]}
        />
      ) : (
        <StatusMessage status={section.status} noneText="Không thể phá huỷ." />
      )}
    </Section>
  );
}

function VisualSection({ details, titleId, item }: { details: StructureDetails; titleId: string; item: ItemListEntry }) {
  const section = details.visual;
  const image = section.image;
  return (
    <Section id={`${titleId}-visual`} title="Hình ảnh">
      {section.status === "known" ? (
        <div className="flex items-center gap-4 p-4">
          {image ? (
            <Image
              src={image.src}
              alt={image.title ?? `Ảnh ${item.name}`}
              width={image.width ?? 160}
              height={image.height ?? 160}
              unoptimized
              className="max-h-44 w-auto rounded-xl border border-[#d5dde6] bg-white object-contain p-2"
            />
          ) : (
            <GameSprite sprite={section.sprite ?? item.sprite} size={112} label={`Ảnh ${item.name}`} />
          )}
        </div>
      ) : (
        <StatusMessage status={section.status} reason={section.reason} noneText="Không có ảnh riêng." />
      )}
    </Section>
  );
}

export function StructureSections({
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
  const details = item.structureDetails;
  if (!details) return null;
  return (
    <div className="space-y-4">
      <OriginSection details={details} titleId={titleId} />
      <ConstructionSection
        details={details}
        titleId={titleId}
        itemsById={itemsById}
        onSelectItem={onSelectItem}
      />
      <FunctionsSection details={details} titleId={titleId} />
      <CraftablesSection
        details={details}
        titleId={titleId}
        itemsById={itemsById}
        onSelectItem={onSelectItem}
      />
      <DestructionSection details={details} titleId={titleId} />
      <VisualSection details={details} titleId={titleId} item={item} />
    </div>
  );
}
