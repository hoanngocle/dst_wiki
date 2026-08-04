import type {
  ItemDetailStatus,
  ItemDropSource,
  ItemListEntry,
  ItemReference,
  ItemUsageRecipe,
} from "@/app/lib/item-catalog";
import { GameSprite } from "./game-sprite";
import { RecipeIngredients } from "./recipe-ingredients";


const DROP_TYPE_LABEL = {
  drop: "Rơi từ",
  harvest: "Thu hoạch từ",
  start: "Vật phẩm khởi đầu",
  trade: "Trao đổi từ",
  other: "Nhận từ",
} as const;

function DetailSection({
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
      className="overflow-hidden rounded-2xl border border-nova-border bg-nova-surface-soft"
    >
      <h3
        id={id}
        className="border-b border-nova-border px-4 py-3 text-sm font-semibold text-nova-text"
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
  status: Exclude<ItemDetailStatus, "known">;
  noneText: string;
}) {
  return (
    <p className="px-4 py-4 text-sm leading-6 text-nova-muted">
      {status === "unknown" ? "Chưa xác định từ dữ liệu mod." : noneText}
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
      <GameSprite sprite={target?.sprite ?? reference.sprite} size={32} />
      <span>{target?.name ?? reference.name}</span>
    </>
  );

  if (!target) {
    return (
      <span className="inline-flex min-h-10 items-center gap-2 rounded-xl px-1.5 py-1 font-semibold text-nova-text">
        {content}
      </span>
    );
  }

  return (
    <button
      type="button"
      aria-label={target.name}
      onClick={() => onSelectItem(target)}
      className="inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-xl px-1.5 py-1 font-semibold text-nova-text transition hover:bg-nova-accent/10 hover:text-nova-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent"
    >
      {content}
    </button>
  );
}

function CraftingSection({
  item,
  titleId,
  itemsById,
  onSelectItem,
}: {
  item: ItemListEntry;
  titleId: string;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  const details = item.details;
  if (!details) return null;

  return (
    <DetailSection id={`${titleId}-crafting`} title="Công thức">
      {details.recipeStatus === "known" && item.recipe ? (
        <>
          <div className="flex flex-wrap items-center gap-3 p-4">
            <RecipeIngredients
              recipe={item.recipe}
              itemsById={itemsById}
              onSelectItem={onSelectItem}
            />
            <span aria-hidden="true" className="text-lg font-semibold text-nova-muted">
              =
            </span>
            <span
              aria-label={`Kết quả: ${item.name}, số lượng ${item.recipe.outputCount}`}
              className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-nova-accent/30 bg-nova-accent/10 py-1 pl-1 pr-3 text-sm font-semibold text-nova-text"
            >
              <GameSprite sprite={item.sprite} size={32} />
              <span>{item.name}</span>
              {item.recipe.outputCount > 1 ? <span>×{item.recipe.outputCount}</span> : null}
            </span>
          </div>
          {item.craftingNote ? (
            <p className="border-t border-nova-border px-4 py-3 text-sm leading-6 text-nova-muted">
              {item.craftingNote}
            </p>
          ) : null}
        </>
      ) : (
        <StatusMessage
          status={details.recipeStatus === "known" ? "unknown" : details.recipeStatus}
          noneText="Không có công thức chế tạo."
        />
      )}
    </DetailSection>
  );
}

function UsageRecipe({
  recipe,
  itemsById,
  onSelectItem,
}: {
  recipe: ItemUsageRecipe;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  return (
    <li className="rounded-xl border border-nova-border bg-nova-surface-raised p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.08em] text-nova-muted">
        Dùng ×{recipe.subjectAmount} để chế tạo
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-sm">
        <ReferenceButton
          reference={recipe.result}
          itemsById={itemsById}
          onSelectItem={onSelectItem}
        />
        {recipe.resultAmount > 1 ? (
          <span className="font-mono text-xs font-semibold text-nova-muted">
            ×{recipe.resultAmount}
          </span>
        ) : null}
      </div>
      {recipe.ingredients.length ? (
        <div className="mt-2 flex flex-wrap gap-2 text-xs text-nova-muted">
          {recipe.ingredients.map((ingredient) => (
            <span
              key={`${recipe.result.id}:${ingredient.id}`}
              className="rounded-lg bg-nova-surface-raised px-2 py-1"
            >
              {ingredient.name} ×{ingredient.amount}
            </span>
          ))}
        </div>
      ) : null}
      {recipe.craftingNote ? (
        <p className="mt-2 text-xs leading-5 text-nova-muted">{recipe.craftingNote}</p>
      ) : null}
    </li>
  );
}

function UsageSection({
  item,
  titleId,
  itemsById,
  onSelectItem,
}: {
  item: ItemListEntry;
  titleId: string;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  const usage = item.details?.usage;
  if (!usage) return null;

  return (
    <DetailSection id={`${titleId}-usage`} title="Usage">
      {usage.status === "known" ? (
        <div className="space-y-3 p-4">
          {usage.effects.length ? (
            <ul className="space-y-2">
              {usage.effects.map((effect) => (
                <li
                  key={`${effect.trigger}:${effect.text}`}
                  className="rounded-xl border border-nova-border bg-nova-surface-raised px-3 py-2.5 text-sm leading-6 text-nova-muted"
                >
                  {effect.text}
                </li>
              ))}
            </ul>
          ) : null}
          {usage.recipes.length ? (
            <ul className="space-y-2">
              {usage.recipes.map((recipe) => (
                <UsageRecipe
                  key={recipe.result.id}
                  recipe={recipe}
                  itemsById={itemsById}
                  onSelectItem={onSelectItem}
                />
              ))}
            </ul>
          ) : null}
        </div>
      ) : (
        <StatusMessage status={usage.status} noneText="Không có cách sử dụng đã biết." />
      )}
    </DetailSection>
  );
}

function DropSourceRow({
  source,
  itemsById,
  onSelectItem,
}: {
  source: ItemDropSource;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  return (
    <li className="grid gap-2 rounded-xl border border-nova-border bg-nova-surface-raised p-3 text-sm sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
      <div className="min-w-0">
        <p className="text-xs font-semibold uppercase tracking-[0.08em] text-nova-muted">
          {DROP_TYPE_LABEL[source.type]}
        </p>
        {source.source ? (
          <ReferenceButton
            reference={source.source}
            itemsById={itemsById}
            onSelectItem={onSelectItem}
          />
        ) : (
          <p className="mt-1 font-semibold text-nova-text">
            {source.conditions ?? DROP_TYPE_LABEL[source.type]}
          </p>
        )}
        {source.source && source.conditions ? (
          <p className="mt-1 text-xs leading-5 text-nova-muted">{source.conditions}</p>
        ) : null}
      </div>
      <div className="flex flex-wrap gap-2 text-xs font-semibold text-nova-muted">
        {source.quantity ? (
          <span className="rounded-lg bg-nova-surface-raised px-2 py-1">{source.quantity}</span>
        ) : null}
        {source.chance ? (
          <span className="rounded-lg bg-nova-accent/10 px-2 py-1 text-nova-accent">
            {source.chance}
          </span>
        ) : null}
      </div>
    </li>
  );
}

function DropBySection({
  item,
  titleId,
  itemsById,
  onSelectItem,
}: {
  item: ItemListEntry;
  titleId: string;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  const dropBy = item.details?.dropBy;
  if (!dropBy) return null;

  return (
    <DetailSection id={`${titleId}-drop-by`} title="Nguồn nhận">
      {dropBy.status === "known" ? (
        <ul className="space-y-2 p-4">
          {dropBy.sources.map((source, index) => (
            <DropSourceRow
              key={`${source.type}:${source.source?.id ?? "none"}:${index}`}
              source={source}
              itemsById={itemsById}
              onSelectItem={onSelectItem}
            />
          ))}
        </ul>
      ) : (
        <StatusMessage
          status={dropBy.status}
          noneText="Không có nguồn nhận ngoài chế tạo."
        />
      )}
    </DetailSection>
  );
}

function CharacterSections({ item, titleId }: { item: ItemListEntry; titleId: string }) {
  const profile = item.character;
  if (!profile) return null;
  return (
    <>
      <DetailSection id={`${titleId}-profile`} title="Hồ sơ nhân vật">
        <dl className="grid gap-px bg-nova-border sm:grid-cols-2">
          <div className="bg-nova-surface-raised px-4 py-3">
            <dt className="text-xs font-semibold text-nova-muted">Danh hiệu</dt>
            <dd className="mt-1 font-semibold text-nova-text">{profile.title ?? "Chưa có dữ liệu"}</dd>
          </div>
          <div className="bg-nova-surface-raised px-4 py-3">
            <dt className="text-xs font-semibold text-nova-muted">Độ sinh tồn</dt>
            <dd className="mt-1 font-semibold text-nova-text">{profile.survivability ?? "Chưa có dữ liệu"}</dd>
          </div>
        </dl>
        {profile.quote ? <blockquote className="border-t border-nova-border bg-nova-surface-raised px-4 py-4 text-sm italic leading-6 text-nova-muted">{profile.quote}</blockquote> : null}
      </DetailSection>
      <DetailSection id={`${titleId}-abilities`} title="Đặc điểm / năng lực">
        {profile.abilities.length ? (
          <ul className="space-y-2 p-4">
            {profile.abilities.map((ability) => (
              <li key={ability} className="rounded-xl border border-nova-border bg-nova-surface-raised px-3 py-2.5 text-sm leading-6 text-nova-muted">{ability}</li>
            ))}
          </ul>
        ) : (
          <p className="px-4 py-4 text-sm leading-6 text-nova-muted">Chưa tìm thấy mô tả năng lực trong dữ liệu mod.</p>
        )}
      </DetailSection>
    </>
  );
}

export function TuTienItemSections({
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
  if (item.namespace !== "tu_tien" || !item.details) return null;

  if (item.category === "character") {
    return <CharacterSections item={item} titleId={titleId} />;
  }

  return (
    <>
      <CraftingSection
        item={item}
        titleId={titleId}
        itemsById={itemsById}
        onSelectItem={onSelectItem}
      />
      <UsageSection
        item={item}
        titleId={titleId}
        itemsById={itemsById}
        onSelectItem={onSelectItem}
      />
      <DropBySection
        item={item}
        titleId={titleId}
        itemsById={itemsById}
        onSelectItem={onSelectItem}
      />
    </>
  );
}
