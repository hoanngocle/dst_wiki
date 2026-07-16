"use client";

import { ArrowSquareOut } from "@phosphor-icons/react";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import type {
  NormalizedWikiReference,
  NormalizedWikiSections,
  NormalizedWikiUsageRecipe,
} from "@/app/lib/wiki-detail";
import { GameSprite } from "./game-sprite";


function WikiReference({
  reference,
  itemsById,
  onSelectItem,
}: {
  reference: NormalizedWikiReference;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  const item = reference.entityId ? itemsById.get(reference.entityId) : undefined;
  if (item) {
    return (
      <button
        type="button"
        onClick={() => onSelectItem(item)}
        className="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-xl px-1.5 py-1 text-left font-semibold text-[#263b58] transition hover:bg-[#e9f1fb] hover:text-[#2e5fb3] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/30"
      >
        <GameSprite sprite={item.sprite} size={30} />
        <span>{item.name}</span>
      </button>
    );
  }

  return (
    <a
      href={reference.url}
      target="_blank"
      rel="noreferrer"
      className="inline-flex min-h-11 items-center gap-1.5 rounded-lg px-1.5 py-1 font-semibold text-[#2e5fb3] transition hover:bg-[#e9f1fb] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/30"
    >
      <span>{reference.title}</span>
      <ArrowSquareOut aria-hidden="true" size={14} />
    </a>
  );
}

function groupRecipes(recipes: readonly NormalizedWikiUsageRecipe[]) {
  const groups = new Map<string, NormalizedWikiUsageRecipe[]>();
  for (const recipe of recipes) {
    const name = recipe.dlc ?? "Don't Starve";
    const group = groups.get(name) ?? [];
    group.push(recipe);
    groups.set(name, group);
  }
  return [...groups.entries()];
}

export function WikiStructuredSections({
  sections,
  itemsById,
  onSelectItem,
}: {
  sections: NormalizedWikiSections;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  return (
    <div className="space-y-4">
      <section className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[#d5dde6] px-4 py-3 sm:px-5">
          <h3 className="font-semibold text-[#172943]">Drop table</h3>
          <p className="font-mono text-xs font-semibold text-[#607188]">
            {sections.dropTable.rows.length} nguồn từ Wiki
          </p>
        </div>
        <ul className="grid grid-cols-1 gap-3 p-4 md:grid-cols-2">
          {sections.dropTable.rows.map((row, index) => (
            <li
              key={`${row.sources.map((source) => source.url).join(":")}:${index}`}
              className="rounded-xl border border-[#d5dde6] bg-[#eef3f8] p-3"
            >
              <div className="flex flex-wrap gap-x-1 gap-y-0">
                {row.sources.map((source) => (
                  <WikiReference
                    key={source.url}
                    reference={source}
                    itemsById={itemsById}
                    onSelectItem={onSelectItem}
                  />
                ))}
              </div>
              <dl className="mt-2 grid grid-cols-2 gap-2">
                <div className="rounded-lg bg-[#f8fafc] px-2.5 py-2">
                  <dt className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[#607188]">
                    Số lượng
                  </dt>
                  <dd className="mt-1 font-mono text-sm font-semibold text-[#172943]">
                    {row.quantity}
                  </dd>
                </div>
                <div className="rounded-lg bg-[#f8fafc] px-2.5 py-2">
                  <dt className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[#607188]">
                    Tỷ lệ
                  </dt>
                  <dd className="mt-1 font-mono text-sm font-semibold text-[#172943]">
                    {row.chance}
                  </dd>
                </div>
              </dl>
              {row.context ? (
                <p className="mt-2 text-xs leading-5 text-[#53647a]">{row.context}</p>
              ) : null}
            </li>
          ))}
        </ul>
      </section>

      <section className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[#d5dde6] px-4 py-3 sm:px-5">
          <h3 className="font-semibold text-[#172943]">Usage</h3>
          <p className="font-mono text-xs font-semibold text-[#607188]">
            {sections.usage.recipes.length} công thức từ Wiki
          </p>
        </div>
        <div className="space-y-5 p-4 sm:p-5">
          {groupRecipes(sections.usage.recipes).map(([group, recipes]) => (
            <section key={group} aria-labelledby={`wiki-usage-${group.replace(/\W+/g, "-")}`}>
              <h4
                id={`wiki-usage-${group.replace(/\W+/g, "-")}`}
                className="text-sm font-semibold text-[#43556d]"
              >
                {group}
              </h4>
              <ul className="mt-2 grid grid-cols-1 gap-3 md:grid-cols-2">
                {recipes.map((recipe, index) => (
                  <li
                    key={`${recipe.result.url}:${index}`}
                    className="rounded-xl border border-[#d5dde6] bg-[#eef3f8] p-3"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <WikiReference
                        reference={recipe.result}
                        itemsById={itemsById}
                        onSelectItem={onSelectItem}
                      />
                      {recipe.resultAmount > 1 ? (
                        <span className="shrink-0 font-mono text-xs font-semibold text-[#43556d]">
                          ×{recipe.resultAmount}
                        </span>
                      ) : null}
                    </div>
                    <div className="mt-2 rounded-lg bg-[#f8fafc] px-2.5 py-2 text-xs text-[#53647a]">
                      <span className="font-semibold text-[#263b58]">Nightmare Fuel</span>
                      <span className="ml-1 font-mono">×{recipe.nightmareFuelAmount}</span>
                    </div>
                    {recipe.ingredients.length ? (
                      <div className="mt-2 flex flex-wrap items-center gap-x-1 gap-y-0 text-sm">
                        {recipe.ingredients.map((ingredient) => (
                          <span
                            key={ingredient.item.url}
                            className="inline-flex items-center gap-1"
                          >
                            <WikiReference
                              reference={ingredient.item}
                              itemsById={itemsById}
                              onSelectItem={onSelectItem}
                            />
                            <span className="font-mono text-xs font-semibold text-[#607188]">
                              ×{ingredient.amount}
                            </span>
                          </span>
                        ))}
                      </div>
                    ) : null}
                    {recipe.station || recipe.character ? (
                      <dl className="mt-2 grid gap-1 text-xs leading-5 text-[#53647a]">
                        {recipe.station ? (
                          <div className="flex gap-2">
                            <dt className="font-semibold text-[#43556d]">Trạm:</dt>
                            <dd>{recipe.station}</dd>
                          </div>
                        ) : null}
                        {recipe.character ? (
                          <div className="flex gap-2">
                            <dt className="font-semibold text-[#43556d]">Nhân vật:</dt>
                            <dd>{recipe.character}</dd>
                          </div>
                        ) : null}
                      </dl>
                    ) : null}
                    {recipe.note ? (
                      <p className="mt-2 text-xs leading-5 text-[#53647a]">{recipe.note}</p>
                    ) : null}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </section>
    </div>
  );
}
