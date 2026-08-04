"use client";

import { CheckIcon } from "@phosphor-icons/react/dist/icons/Check";
import { MagnifyingGlassIcon } from "@phosphor-icons/react/dist/icons/MagnifyingGlass";
import { XIcon } from "@phosphor-icons/react/dist/icons/X";
import { useMemo, useState } from "react";

import { DstField, dstControlClassName } from "@/app/components/dst-field";
import { DstHero } from "@/app/components/dst-hero";
import { DstPanel } from "@/app/components/dst-panel";
import { DstState } from "@/app/components/dst-state";
import {
  filterCharacters,
  type CharacterCatalogEntry,
  type CharacterFilters,
} from "@/app/lib/character-catalog";
import { CharacterCard } from "./character-card";
import { CharacterDossierModal } from "./character-dossier-modal";

type CharacterGalleryProps = {
  characters: readonly CharacterCatalogEntry[];
};

const sourceFilters: ReadonlyArray<{
  value: NonNullable<CharacterFilters["namespace"]>;
  label: string;
}> = [
  { value: "all", label: "Tất cả" },
  { value: "tu_tien", label: "Tu Tiên" },
  { value: "base_game", label: "DST gốc" },
];

export function CharacterGallery({ characters }: CharacterGalleryProps) {
  const [query, setQuery] = useState("");
  const [namespace, setNamespace] =
    useState<NonNullable<CharacterFilters["namespace"]>>("all");
  const [selectedCharacter, setSelectedCharacter] =
    useState<CharacterCatalogEntry | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const filteredCharacters = useMemo(
    () => filterCharacters(characters, { query, namespace }),
    [characters, namespace, query],
  );
  const sourceTotals = useMemo(() => {
    let tuTien = 0;
    let dst = 0;
    for (const character of characters) {
      if (character.namespace === "tu_tien") tuTien += 1;
      else dst += 1;
    }
    return { tuTien, dst };
  }, [characters]);
  const hasActiveControls = query.trim() !== "" || namespace !== "all";

  function dismissDossier() {
    setModalOpen(false);
    setSelectedCharacter(null);
  }

  function resetFilters() {
    dismissDossier();
    setQuery("");
    setNamespace("all");
  }

  return (
    <>
      <div data-testid="character-catalog" className="grow text-nova-text">
        <DstHero
          testId="character-catalog-header"
          eyebrow="Bách khoa nhân vật"
          title="Chọn nhân vật theo lối chơi"
          description="So sánh chỉ số, năng lực và pháp bảo trước khi mở hồ sơ chiến thuật đầy đủ."
          stats={[
            {
              label: "Nhân vật",
              value: <span data-testid="character-total">{characters.length}</span>,
            },
            {
              label: "Tu Tiên",
              value: (
                <span data-testid="character-tu-tien-total">{sourceTotals.tuTien}</span>
              ),
            },
            {
              label: "DST",
              value: <span data-testid="character-dst-total">{sourceTotals.dst}</span>,
            },
          ]}
          statsAriaLabel="Tổng quan nhân vật"
        />

        <section aria-label="Tìm và lọc nhân vật" className="pt-6">
          <DstPanel testId="character-filter-panel" className="overflow-hidden">
            <div className="grid gap-4 p-4 lg:grid-cols-[minmax(18rem,1fr)_auto] lg:items-end lg:p-5">
              <DstField label="Tìm nhân vật" htmlFor="character-search">
                <div className="relative">
                  <MagnifyingGlassIcon
                    aria-hidden="true"
                    size={20}
                    className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-nova-faint"
                  />
                  <input
                    id="character-search"
                    type="search"
                    value={query}
                    onChange={(event) => {
                      dismissDossier();
                      setQuery(event.target.value);
                    }}
                    placeholder="Tên Việt, tên Anh, code hoặc vai trò"
                    className={`${dstControlClassName} py-2.5 pl-12 pr-4`}
                  />
                </div>
              </DstField>
              <div
                role="group"
                aria-label="Lọc theo nguồn nhân vật"
                className="flex flex-wrap gap-2"
              >
                {sourceFilters.map((filter) => (
                  <button
                    key={filter.value}
                    type="button"
                    aria-label={filter.label}
                    aria-pressed={namespace === filter.value}
                    onClick={() => {
                      dismissDossier();
                      setNamespace(filter.value);
                    }}
                    className="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-xl border border-nova-border bg-nova-surface-soft px-4 text-sm font-semibold text-nova-muted transition-colors hover:text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent aria-pressed:border-nova-accent aria-pressed:text-nova-accent"
                  >
                    <span className="inline-flex size-4 items-center justify-center">
                      {namespace === filter.value ? (
                        <CheckIcon aria-hidden="true" size={16} weight="bold" />
                      ) : null}
                    </span>
                    {filter.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex min-h-11 flex-wrap items-center justify-between gap-3 border-t border-nova-border px-4 py-2 lg:px-5">
              <p role="status" aria-live="polite" className="text-sm font-semibold text-nova-muted">
                {filteredCharacters.length} nhân vật
              </p>
              {hasActiveControls ? (
                <button
                  type="button"
                  onClick={resetFilters}
                  aria-label="Đặt lại tìm kiếm và bộ lọc"
                  className="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-lg px-3 text-sm font-semibold text-nova-muted hover:bg-nova-surface-soft hover:text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent"
                >
                  <XIcon aria-hidden="true" size={16} />
                  Đặt lại
                </button>
              ) : null}
            </div>
          </DstPanel>

          {filteredCharacters.length > 0 ? (
            <div
              data-testid="character-grid"
              className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3"
            >
              {filteredCharacters.map((character, index) => (
                <CharacterCard
                  key={character.id}
                  character={character}
                  revealOrder={index}
                  onOpen={(selected) => {
                    setSelectedCharacter(selected);
                    setModalOpen(true);
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="mt-5">
              <DstState
                tone="empty"
                title="Không tìm thấy nhân vật phù hợp."
                actions={
                  hasActiveControls ? (
                    <button
                      type="button"
                      onClick={resetFilters}
                      className="min-h-11 cursor-pointer rounded-xl border border-nova-border bg-nova-surface-soft px-4 text-sm font-semibold text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent"
                    >
                      Đặt lại
                    </button>
                  ) : undefined
                }
              />
            </div>
          )}
        </section>
      </div>

      <CharacterDossierModal
        character={selectedCharacter}
        open={modalOpen}
        onOpenChange={(open) => {
          setModalOpen(open);
          if (!open) setSelectedCharacter(null);
        }}
      />
    </>
  );
}
