import { XIcon } from "@phosphor-icons/react/dist/icons/X";
import Image from "next/image";
import { useRef } from "react";

import type { CharacterCatalogEntry } from "@/app/lib/character-catalog";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/app/components/ui/dialog";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/app/components/ui/tabs";
import { CharacterArtifacts } from "./character-artifacts";
import { CharacterCombat } from "./character-combat";
import { CharacterOverview } from "./character-overview";
import { CharacterRealms } from "./character-realms";

type CharacterDossierModalProps = {
  character: CharacterCatalogEntry | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

const dossierTabs = [
  { value: "overview", label: "Tổng quan" },
  { value: "combat", label: "Chiến đấu" },
  { value: "realms", label: "Cảnh giới" },
  { value: "artifacts", label: "Pháp bảo" },
] as const;

const dialogClassName =
  "nova-game-theme fixed left-0 top-0 h-svh max-h-svh w-screen max-w-none translate-x-0 translate-y-0 overflow-hidden rounded-none border-0 bg-nova-surface-raised text-nova-text shadow-[0_28px_90px_rgba(0,0,0,0.5)] sm:left-1/2 sm:top-1/2 sm:h-[min(90svh,900px)] sm:max-h-[calc(100svh-2rem)] sm:w-[calc(100%-2rem)] sm:max-w-[64rem] sm:-translate-x-1/2 sm:-translate-y-1/2 sm:rounded-xl sm:border sm:border-nova-border";

export function CharacterDossierModal({
  character,
  open,
  onOpenChange,
}: CharacterDossierModalProps) {
  const overviewTabRef = useRef<HTMLButtonElement>(null);
  const returnFocusRef = useRef<HTMLElement | null>(null);

  if (!character) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        aria-modal="true"
        centered={false}
        data-testid="character-dossier-shell"
        showCloseButton={false}
        overlayClassName="bg-black/70 motion-reduce:animate-none"
        style={{ minHeight: "auto", backgroundColor: "var(--nova-surface-raised)" }}
        onOpenAutoFocus={(event) => {
          const activeElement = document.activeElement;
          if (activeElement instanceof HTMLElement) {
            returnFocusRef.current = activeElement;
          }
          event.preventDefault();
          overviewTabRef.current?.focus();
        }}
        onCloseAutoFocus={(event) => {
          event.preventDefault();
          returnFocusRef.current?.focus();
        }}
        className={`${dialogClassName} gap-0 p-0 motion-reduce:transition-none`}
      >
        <Tabs
          key={`${character.id}:${open ? "open" : "closed"}`}
          defaultValue="overview"
          activationMode="automatic"
          className="flex min-h-0 flex-1 flex-col"
        >
          <header className="sticky top-0 z-20 shrink-0 border-b border-nova-border bg-nova-surface-raised">
            <div className="grid grid-cols-[4rem_minmax(0,1fr)_2.75rem] items-center gap-3 px-3 py-3 sm:grid-cols-[6rem_minmax(0,1fr)_2.75rem] sm:gap-5 sm:px-6 sm:py-4">
              <div className="aspect-square overflow-hidden rounded-xl bg-nova-surface-soft ring-1 ring-nova-border">
                <Image
                  src={character.portrait}
                  alt=""
                  width={640}
                  height={800}
                  unoptimized
                  decoding="async"
                  className="h-full w-full object-contain"
                />
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-nova-accent">
                  {character.namespace === "tu_tien" ? "Tu Tiên" : "DST"}
                </p>
                <DialogTitle className="mt-1 truncate text-xl leading-tight tracking-tight text-nova-text sm:text-3xl">
                  {character.name}
                </DialogTitle>
                <DialogDescription className="mt-1 line-clamp-2 leading-relaxed">
                  {character.title || character.description || "Hồ sơ chiến thuật nhân vật"}
                </DialogDescription>
              </div>
              <DialogClose
                aria-label="Đóng hồ sơ"
                className="inline-flex min-h-11 min-w-11 cursor-pointer items-center justify-center rounded-xl border border-nova-border bg-nova-surface-soft text-nova-muted transition-colors hover:text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-nova-accent motion-reduce:transition-none"
              >
                <XIcon aria-hidden="true" size={20} />
              </DialogClose>
            </div>
            <TabsList
              aria-label="Các mục hồ sơ nhân vật"
              className="min-h-11 w-full overflow-x-auto border-t border-nova-border px-2 sm:px-5"
            >
              {dossierTabs.map((tab) => (
                <TabsTrigger
                  key={tab.value}
                  ref={tab.value === "overview" ? overviewTabRef : undefined}
                  value={tab.value}
                  className="relative shrink-0 px-4 text-sm font-semibold text-nova-muted transition-colors after:absolute after:bottom-0 after:left-4 after:right-4 after:h-0.5 after:scale-x-0 after:bg-nova-accent after:transition-transform hover:text-nova-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-nova-accent data-[state=active]:text-nova-text data-[state=active]:after:scale-x-100 motion-reduce:transition-none motion-reduce:after:transition-none"
                >
                  {tab.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </header>
          <div
            data-testid="character-dossier-scroll-area"
            className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-4 py-6 sm:px-8 sm:py-8"
          >
            <TabsContent value="overview">
              <CharacterOverview character={character} />
            </TabsContent>
            <TabsContent value="combat">
              <CharacterCombat character={character} />
            </TabsContent>
            <TabsContent value="realms">
              <CharacterRealms character={character} />
            </TabsContent>
            <TabsContent value="artifacts">
              <CharacterArtifacts character={character} />
            </TabsContent>
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
