import { CharacterGallery } from "@/app/components/characters/character-gallery";
import { DstPageShell } from "@/app/components/dst-page-shell";
import { SiteHeader } from "@/app/components/site-header";
import {
  buildCharacterCatalog,
  parseCharacterGuides,
  parseCharacterProfiles,
} from "@/app/lib/character-catalog";
import { parseItemPayload } from "@/app/lib/item-catalog";
import guidePayload from "@/data/manual/character-guides.json";
import profilePayload from "@/data/manual/character-profiles.json";
import itemPayload from "@/public/data/items.json";

const characters = buildCharacterCatalog(
  parseItemPayload(itemPayload),
  parseCharacterProfiles(profilePayload),
  parseCharacterGuides(guidePayload),
  "vi",
);

export default function CharactersPage() {
  return (
    <div className="min-h-[100dvh] bg-nova-bg text-nova-text">
      <SiteHeader active="characters" />
      <DstPageShell>
        <div className="px-4 py-9 sm:px-6 sm:py-12 lg:px-8">
          <CharacterGallery characters={characters} />
        </div>
      </DstPageShell>
    </div>
  );
}
