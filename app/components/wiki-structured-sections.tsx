"use client";

import { ArrowSquareOut } from "@phosphor-icons/react";
import Image from "next/image";
import { useId, useMemo } from "react";

import type { ItemListEntry } from "@/app/lib/item-catalog";
import type {
  NormalizedWikiReference,
  NormalizedWikiSections,
  NormalizedWikiUsageRecipe,
} from "@/app/lib/wiki-detail";
import { GameSprite } from "./game-sprite";

const WIKI_PAGE_BASE = "https://dontstarve.wiki.gg/wiki/";
const WIKI_FILE_BASE = `${WIKI_PAGE_BASE}Special:Redirect/file/`;
const STRUCTURED_ICON_SIZE = 48;

const NIGHTMARE_FUEL_REFERENCE: NormalizedWikiReference = {
  title: "Nightmare Fuel",
  url: `${WIKI_PAGE_BASE}Nightmare_Fuel`,
  entityId: null,
  iconUrl: `${WIKI_FILE_BASE}Nightmare_Fuel.png`,
};

const STATION_ICON_FILES: Readonly<Record<string, string>> = {
  "Ancient Pseudoscience Station": "AncientAltar.png",
};

const STATION_ICON_URLS: Readonly<Record<string, string>> = {
  "Broken Pseudoscience Station":
    "https://dontstarve.wiki.gg/images/thumb/Navbox_Broken_Pseudoscience_Station.png/50px-Navbox_Broken_Pseudoscience_Station.png?926476",
};

const HIDDEN_USAGE_DLC_PATTERN = /\b(?:shipwrecked|hamlet)\b/i;

function normalizedTitle(value: string) {
  return value.trim().toLocaleLowerCase("en");
}

function wikiPageUrl(title: string) {
  return WIKI_PAGE_BASE + encodeURIComponent(title.replaceAll(" ", "_")).replaceAll("%2F", "/");
}

function wikiFileUrl(title: string) {
  const filename = /\.(?:gif|jpe?g|png|webp)$/i.test(title) ? title : `${title}.png`;
  return WIKI_FILE_BASE + encodeURIComponent(filename.replaceAll(" ", "_"));
}

function stationReference(station: string): NormalizedWikiReference {
  const pageTitle =
    station === "Broken Pseudoscience Station"
      ? "Ancient Pseudoscience Station"
      : station;
  return {
    title: station,
    url: wikiPageUrl(pageTitle),
    entityId: null,
    iconUrl:
      STATION_ICON_URLS[station] ?? wikiFileUrl(STATION_ICON_FILES[station] ?? station),
  };
}

function indexItemsByTitle(itemsById: ReadonlyMap<string, ItemListEntry>) {
  const result = new Map<string, ItemListEntry>();
  for (const item of itemsById.values()) {
    for (const title of [item.name, item.englishName, item.wiki?.title]) {
      if (!title) continue;
      const key = normalizedTitle(title);
      const existing = result.get(key);
      if (!existing || (!existing.sprite && item.sprite)) result.set(key, item);
    }
  }
  return result;
}

function WikiUsageIcon({
  reference,
  amount,
  itemsById,
  itemsByTitle,
  onSelectItem,
}: {
  reference: NormalizedWikiReference;
  amount?: number;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  itemsByTitle: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
}) {
  const tooltipId = useId();
  const item =
    (reference.entityId ? itemsById.get(reference.entityId) : undefined) ??
    itemsByTitle.get(normalizedTitle(reference.title));
  const displayTitle = item?.name ?? reference.title;
  const accessibleName =
    amount === undefined
      ? displayTitle
      : `${displayTitle}, số lượng ${amount}`;
  const image = item?.sprite ? (
    <GameSprite
      sprite={item.sprite}
      size={STRUCTURED_ICON_SIZE}
      rounded={false}
      className="rounded-[4px]"
    />
  ) : (
    <Image
      src={reference.iconUrl ?? wikiFileUrl(reference.title)}
      alt=""
      width={STRUCTURED_ICON_SIZE}
      height={STRUCTURED_ICON_SIZE}
      data-testid="wiki-usage-icon"
      className="size-[48px] shrink-0 rounded-[4px] border border-[#c8d3df] bg-[#e5ebf1] object-contain"
    />
  );
  const content = (
    <>
      {image}
      {amount === undefined ? null : (
        <span aria-hidden="true" className="font-mono text-xs font-semibold text-[#53647a]">
          ×{amount}
        </span>
      )}
      <span
        id={tooltipId}
        role="tooltip"
        className="pointer-events-none invisible absolute left-1/2 top-full z-20 mt-2 -translate-x-1/2 whitespace-nowrap rounded-lg bg-[#172943] px-2.5 py-1.5 text-xs font-medium text-white opacity-0 shadow-lg transition group-hover:visible group-hover:opacity-100 group-focus-visible:visible group-focus-visible:opacity-100"
      >
        {displayTitle}
      </span>
    </>
  );
  const className =
    "group relative inline-flex min-h-10 items-center gap-1.5 rounded-xl border border-transparent px-1.5 py-1 transition hover:border-[#b9cce8] hover:bg-[#e9f1fb] focus-visible:border-[#2e5fb3] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/30 active:scale-[0.98]";

  if (item) {
    return (
      <button
        type="button"
        aria-label={accessibleName}
        aria-describedby={tooltipId}
        onClick={() => onSelectItem(item)}
        className={`${className} cursor-pointer`}
      >
        {content}
      </button>
    );
  }

  return (
    <a
      href={reference.url}
      target="_blank"
      rel="noreferrer"
      aria-label={accessibleName}
      aria-describedby={tooltipId}
      className={className}
    >
      {content}
    </a>
  );
}

function WikiReference({
  reference,
  itemsById,
  onSelectItem,
  showFallbackIcon = false,
}: {
  reference: NormalizedWikiReference;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
  showFallbackIcon?: boolean;
}) {
  const item = reference.entityId ? itemsById.get(reference.entityId) : undefined;
  if (item) {
    return (
      <button
        type="button"
        title={item.name}
        onClick={() => onSelectItem(item)}
        className="inline-flex min-h-11 max-w-full cursor-pointer items-center gap-2 whitespace-nowrap rounded-xl px-1.5 py-1 text-left font-semibold text-[#263b58] transition hover:bg-[#e9f1fb] hover:text-[#2e5fb3] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/30"
      >
        <GameSprite
          sprite={item.sprite}
          size={STRUCTURED_ICON_SIZE}
          rounded={false}
          className="rounded-[4px]"
        />
        <span className="min-w-0 truncate">{item.name}</span>
      </button>
    );
  }

  return (
    <a
      href={reference.url}
      target="_blank"
      rel="noreferrer"
      title={reference.title}
      className="inline-flex min-h-11 max-w-full items-center gap-2 whitespace-nowrap rounded-xl px-1.5 py-1 font-semibold text-[#2e5fb3] transition hover:bg-[#e9f1fb] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2e5fb3]/30"
    >
      {showFallbackIcon ? (
        reference.iconUrl ? (
          <Image
            src={reference.iconUrl}
            alt=""
            width={STRUCTURED_ICON_SIZE}
            height={STRUCTURED_ICON_SIZE}
            data-testid="wiki-source-icon"
            className="size-[48px] shrink-0 rounded-[4px] border border-[#c8d3df] bg-[#e5ebf1] object-contain"
          />
        ) : (
          <GameSprite
            sprite={null}
            size={STRUCTURED_ICON_SIZE}
            rounded={false}
            className="rounded-[4px]"
          />
        )
      ) : null}
      <span className="min-w-0 truncate">{reference.title}</span>
      <ArrowSquareOut aria-hidden="true" size={14} className="shrink-0" />
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

function visibleUsageRecipes(recipes: readonly NormalizedWikiUsageRecipe[]) {
  return recipes.filter((recipe) => {
    const dlcContext = `${recipe.dlc ?? ""} ${recipe.note ?? ""}`;
    return !HIDDEN_USAGE_DLC_PATTERN.test(dlcContext);
  });
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
  const itemsByTitle = useMemo(() => indexItemsByTitle(itemsById), [itemsById]);
  const usageRecipes = useMemo(
    () => visibleUsageRecipes(sections.usage.recipes),
    [sections.usage.recipes],
  );

  return (
    <div className="space-y-4">
      <section className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[#d5dde6] px-4 py-3 sm:px-5">
          <h3 className="font-semibold text-[#172943]">Drop table</h3>
          <p className="font-mono text-xs font-semibold text-[#607188]">
            {sections.dropTable.rows.length} nguồn từ Wiki
          </p>
        </div>
        <div className="min-w-0">
          <table aria-label="Drop table" className="w-full table-fixed border-collapse text-left">
            <thead className="bg-[#eaf0f6]">
              <tr className="border-b border-[#c8d3df]">
                <th
                  scope="col"
                  className="w-[58%] px-4 py-2.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-[#607188] sm:px-5"
                >
                  Nguồn
                </th>
                <th
                  scope="col"
                  className="w-[12%] px-4 py-2.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-[#607188]"
                >
                  Số lượng
                </th>
                <th
                  scope="col"
                  className="w-[10%] px-4 py-2.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-[#607188]"
                >
                  Tỷ lệ
                </th>
                <th
                  scope="col"
                  className="w-[20%] px-4 py-2.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-[#607188] sm:pr-5"
                >
                  Điều kiện
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#d5dde6]">
              {sections.dropTable.rows.map((row, index) => (
                <tr
                  key={`${row.sources.map((source) => source.url).join(":")}:${index}`}
                  className="bg-[#f8fafc] align-middle transition-colors hover:bg-[#f1f5f9]"
                >
                  <td className="px-4 py-2 sm:px-5">
                    <div className="flex flex-wrap gap-x-1 gap-y-1">
                      {row.sources.map((source) => (
                        <WikiReference
                          key={source.url}
                          reference={source}
                          itemsById={itemsById}
                          onSelectItem={onSelectItem}
                          showFallbackIcon
                        />
                      ))}
                    </div>
                  </td>
                  <td className="break-words px-4 py-2 font-mono text-sm font-semibold text-[#172943]">
                    {row.quantity}
                  </td>
                  <td className="whitespace-nowrap px-4 py-2 font-mono text-sm font-semibold text-[#172943]">
                    {row.chance}
                  </td>
                  <td className="px-4 py-2 text-xs leading-5 text-[#53647a] sm:pr-5">
                    {row.context ?? <span aria-label="Không có điều kiện">—</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="overflow-hidden rounded-2xl border border-[#c8d3df] bg-[#f8fafc]">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[#d5dde6] px-4 py-3 sm:px-5">
          <h3 className="font-semibold text-[#172943]">Usage</h3>
          <p className="font-mono text-xs font-semibold text-[#607188]">
            {usageRecipes.length} công thức từ Wiki
          </p>
        </div>
        <div className="space-y-5 py-4 sm:py-5">
          {groupRecipes(usageRecipes).map(([group, recipes]) => (
            <section
              key={group}
              aria-label={group === "Don't Starve" ? "Công thức cơ bản" : undefined}
              aria-labelledby={
                group === "Don't Starve"
                  ? undefined
                  : `wiki-usage-${group.replace(/\W+/g, "-")}`
              }
            >
              {group === "Don't Starve" ? null : (
                <h4
                  id={`wiki-usage-${group.replace(/\W+/g, "-")}`}
                  className="px-4 text-sm font-semibold text-[#43556d] sm:px-5"
                >
                  {group}
                </h4>
              )}
              <div
                className={`${group === "Don't Starve" ? "" : "mt-2"} overflow-x-auto border-y border-[#d5dde6]`}
              >
                <table
                  aria-label={`Usage: ${group}`}
                  className="w-full min-w-[760px] border-collapse text-left"
                >
                  <thead className="bg-[#eaf0f6]">
                    <tr className="border-b border-[#c8d3df]">
                      <th
                        scope="col"
                        className="w-[56%] px-4 py-2.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-[#607188] sm:px-5"
                      >
                        Công thức
                      </th>
                      <th
                        scope="col"
                        className="w-[22%] px-4 py-2.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-[#607188]"
                      >
                        Trạm / Nhân vật
                      </th>
                      <th
                        scope="col"
                        className="w-[22%] px-4 py-2.5 text-[11px] font-semibold uppercase tracking-[0.08em] text-[#607188] sm:pr-5"
                      >
                        Thành phẩm
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#d5dde6]">
                    {recipes.map((recipe, index) => (
                      <tr
                        key={`${recipe.result.url}:${index}`}
                        className="bg-[#f8fafc] align-middle transition-colors hover:bg-[#f1f5f9]"
                      >
                        <td className="px-4 py-2 sm:px-5">
                          <div className="flex min-w-max items-center gap-1">
                            <WikiUsageIcon
                              reference={NIGHTMARE_FUEL_REFERENCE}
                              amount={recipe.nightmareFuelAmount}
                              itemsById={itemsById}
                              itemsByTitle={itemsByTitle}
                              onSelectItem={onSelectItem}
                            />
                            {recipe.ingredients.map((ingredient) => (
                              <span
                                key={ingredient.item.url}
                                className="inline-flex items-center gap-1"
                              >
                                <span
                                  aria-hidden="true"
                                  className="font-mono text-sm font-semibold text-[#8290a3]"
                                >
                                  +
                                </span>
                                <WikiUsageIcon
                                  reference={ingredient.item}
                                  amount={ingredient.amount}
                                  itemsById={itemsById}
                                  itemsByTitle={itemsByTitle}
                                  onSelectItem={onSelectItem}
                                />
                              </span>
                            ))}
                          </div>
                          {recipe.note ? (
                            <p className="mt-1 text-xs leading-5 text-[#53647a]">
                              {recipe.note}
                            </p>
                          ) : null}
                        </td>
                        <td className="px-4 py-2">
                          <div className="flex min-h-10 items-center gap-2">
                            {recipe.station ? (
                              <WikiUsageIcon
                                reference={stationReference(recipe.station)}
                                itemsById={itemsById}
                                itemsByTitle={itemsByTitle}
                                onSelectItem={onSelectItem}
                              />
                            ) : null}
                            {recipe.character ? (
                              <span className="whitespace-nowrap text-xs text-[#53647a]">
                                <span className="font-semibold text-[#43556d]">
                                  Nhân vật:
                                </span>{" "}
                                {recipe.character}
                              </span>
                            ) : null}
                            {!recipe.station && !recipe.character ? (
                              <span className="text-xs text-[#8290a3]">Không có</span>
                            ) : null}
                          </div>
                        </td>
                        <td className="px-4 py-2 sm:pr-5">
                          <WikiUsageIcon
                            reference={recipe.result}
                            amount={recipe.resultAmount}
                            itemsById={itemsById}
                            itemsByTitle={itemsByTitle}
                            onSelectItem={onSelectItem}
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ))}
        </div>
      </section>
    </div>
  );
}
